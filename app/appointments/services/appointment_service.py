from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from appointments.models.AppointmentModel import Appointments
from Patient.models.PatientModel import Patient
from appointments.repositories.AppointmentRepository import AppointmentRepository
from appointments.schemas.AppointmentSchema import AppointmentCreate, AppointmentReschedule
from utilityfunctions.encryption import EncryptionService


SLOT_LENGTH = timedelta(minutes=30)
COMPLAINT_CIPHERTEXT_PREFIX = "enc:v1:"


class AppointmentService:
    """Enforce availability, booking, and patient ownership rules."""

    def __init__(self, db: Session):
        self.db = db
        self.appointments = AppointmentRepository(db)
        self.encryption = EncryptionService()

    def _encrypt_complaint(self, complaint: str) -> str:
        encrypted = self.encryption.encrypt(complaint, "appointment_complaint")
        return f"{COMPLAINT_CIPHERTEXT_PREFIX}{encrypted}"

    def _decrypt_complaint(self, complaint: str | None) -> str | None:
        if complaint is None or not complaint.startswith(COMPLAINT_CIPHERTEXT_PREFIX):
            # Keep appointments created before complaint encryption readable.
            return complaint
        return self.encryption.decrypt(
            complaint[len(COMPLAINT_CIPHERTEXT_PREFIX):], "appointment_complaint"
        )

    def _appointment_response(self, appointment: Appointments) -> dict:
        return {
            "AppointmentID": appointment.AppointmentID,
            "patientID": appointment.patientID,
            "DoctorID": appointment.DoctorID,
            "AppointmentDate": appointment.AppointmentDate,
            "AppointmentTime": appointment.AppointmentTime,
            "Complaint": self._decrypt_complaint(appointment.Complaint),
            "Booked_at": appointment.Booked_at,
        }

    def _require_patient(self, patient_id: int) -> None:
        if self.db.get(Patient, patient_id) is None:
            raise HTTPException(status_code=404, detail="Patient not found")

    @staticmethod
    def _check_date(appointment_date: date) -> None:
        if appointment_date < date.today():
            raise HTTPException(status_code=422, detail="Appointment date must be today or later")

    @staticmethod
    def _schedule_time(value: str | time) -> time:
        """Parse a timing stored as TEXT (HH:MM or HH:MM:SS)."""
        if isinstance(value, time):
            return value
        try:
            return time.fromisoformat(value.strip())
        except (AttributeError, ValueError) as exc:
            raise HTTPException(
                status_code=500,
                detail="Doctor schedule contains an invalid time; expected HH:MM or HH:MM:SS",
            ) from exc

    @staticmethod
    def _slot_is_scheduled(start: time, schedule) -> bool:
        if start.second or start.microsecond or (start.minute % 30):
            return False
        slot_start = datetime.combine(date.min, start)
        slot_end = slot_start + SLOT_LENGTH
        return any(
            slot_start >= datetime.combine(date.min, AppointmentService._schedule_time(row.startTime))
            and slot_end <= datetime.combine(date.min, AppointmentService._schedule_time(row.endTime))
            for row in schedule
        )

    def get_available_slots(self, doctor_id: int, appointment_date: date) -> list[time]:
        self._check_date(appointment_date)
        if self.appointments.find_doctor(doctor_id) is None:
            raise HTTPException(status_code=404, detail="Doctor not found")

        weekday = appointment_date.strftime("%A")
        schedule = self.appointments.get_doctor_schedule(doctor_id, weekday)
        booked = self.appointments.get_booked_times(doctor_id, appointment_date)
        available: set[time] = set()
        for row in schedule:
            current = datetime.combine(appointment_date, self._schedule_time(row.startTime))
            end = datetime.combine(appointment_date, self._schedule_time(row.endTime))
            minute_of_day = current.hour * 60 + current.minute
            rounded_minute = ((minute_of_day + 29) // 30) * 30
            if rounded_minute >= 24 * 60:
                continue
            current = datetime.combine(appointment_date, time(rounded_minute // 60, rounded_minute % 60))
            while current + SLOT_LENGTH <= end:
                slot = current.time()
                if slot not in booked:
                    available.add(slot)
                current += SLOT_LENGTH
        return sorted(available)

    def _reserve_slot(self, doctor_id: int, appointment_date: date, appointment_time: time) -> None:
        # Serializes bookings for this doctor while the slot is checked and inserted.
        doctor = self.appointments.find_doctor(doctor_id, lock=True)
        if doctor is None:
            raise HTTPException(status_code=404, detail="Doctor not found")
        self._check_date(appointment_date)
        schedule = self.appointments.get_doctor_schedule(
            doctor_id, appointment_date.strftime("%A")
        )
        if not self._slot_is_scheduled(appointment_time, schedule):
            raise HTTPException(status_code=409, detail="The selected time is outside the doctor's available schedule")
        if appointment_time in self.appointments.get_booked_times(doctor_id, appointment_date):
            raise HTTPException(status_code=409, detail="This appointment slot has already been booked")

    def book_appointment(self, patient_id: int, request: AppointmentCreate) -> dict:
        try:
            self._require_patient(patient_id)
            self._reserve_slot(request.DoctorID, request.AppointmentDate, request.AppointmentTime)
            appointment = Appointments(
                patientID=patient_id,
                DoctorID=request.DoctorID,
                AppointmentDate=request.AppointmentDate,
                AppointmentTime=request.AppointmentTime,
                Complaint=self._encrypt_complaint(request.Complaint),
                Booked_at=datetime.now(),
            )
            self.appointments.create(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            return self._appointment_response(appointment)
        except Exception:
            self.db.rollback()
            raise

    def list_patient_appointments(self, patient_id: int) -> list[dict]:
        self._require_patient(patient_id)
        appointments = self.appointments.list_for_patient(patient_id)
        for appointment in appointments:
            appointment["Complaint"] = self._decrypt_complaint(appointment["Complaint"])
        return appointments

    def cancel_appointment(self, patient_id: int, appointment_id: int) -> None:
        appointment = self.appointments.find_patient_appointment(
            patient_id, appointment_id, lock=True
        )
        if appointment is None:
            raise HTTPException(status_code=404, detail="Appointment not found")
        try:
            self.appointments.delete(appointment)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def reschedule_appointment(
        self, patient_id: int, appointment_id: int, request: AppointmentReschedule
    ) -> dict:
        appointment = self.appointments.find_patient_appointment(
            patient_id, appointment_id, lock=True
        )
        if appointment is None:
            raise HTTPException(status_code=404, detail="Appointment not found")
        try:
            self._reserve_slot(appointment.DoctorID, request.AppointmentDate, request.AppointmentTime)
            if (
                appointment.AppointmentDate == request.AppointmentDate
                and appointment.AppointmentTime == request.AppointmentTime
            ):
                raise HTTPException(status_code=409, detail="Choose a different appointment slot")
            appointment.AppointmentDate = request.AppointmentDate
            appointment.AppointmentTime = request.AppointmentTime
            self.db.commit()
            self.db.refresh(appointment)
            return self._appointment_response(appointment)
        except Exception:
            self.db.rollback()
            raise

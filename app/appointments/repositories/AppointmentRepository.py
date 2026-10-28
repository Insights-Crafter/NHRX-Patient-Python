from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from appointments.models.AppointmentModel import Appointments
from Doctor.models.DoctorAvailbilityModel import DoctorAvailability
from Doctor.models.DoctorModel import Doctor
from Doctor.models.DoctorSpecialities import Specialities
from Hospital.models.HospitalModel import Hospital


class AppointmentRepository:
    """Database access for appointment scheduling and patient bookings."""

    def __init__(self, db: Session):
        self.db = db

    def find_doctor(self, doctor_id: int, *, lock: bool = False):
        statement = select(Doctor).where(Doctor.id == doctor_id)
        if lock:
            statement = statement.with_for_update()
        return self.db.scalar(statement)

    def get_doctor_schedule(self, doctor_id: int, day: str) -> list[DoctorAvailability]:
        statement = select(DoctorAvailability).where(
            DoctorAvailability.doctorId == doctor_id,
            DoctorAvailability.day.ilike(day),
        ).order_by(DoctorAvailability.startTime)
        return list(self.db.scalars(statement).all())

    def get_booked_times(self, doctor_id: int, appointment_date: date) -> set[time]:
        statement = select(Appointments.AppointmentTime).where(
            Appointments.DoctorID == doctor_id,
            Appointments.AppointmentDate == appointment_date,
        )
        return set(self.db.scalars(statement).all())

    def create(self, appointment: Appointments) -> Appointments:
        self.db.add(appointment)
        self.db.flush()
        return appointment

    def list_for_patient(self, patient_id: int) -> list[dict]:
        statement = (
            select(
                Appointments,
                Doctor.name.label("doctorName"),
                Specialities.name.label("specialityName"),
                Hospital.hospitalName.label("hospitalName"),
                Hospital.City.label("City"),
            )
            .join(Doctor, Appointments.DoctorID == Doctor.id)
            .outerjoin(Specialities, Doctor.specialtyId == Specialities.id)
            .outerjoin(Hospital, Doctor.hospitalId == Hospital.hospitalID)
            .where(Appointments.patientID == patient_id)
            .order_by(Appointments.AppointmentDate, Appointments.AppointmentTime)
        )
        results = self.db.execute(statement).all()
        return [
            {
                "AppointmentID": row[0].AppointmentID,
                "patientID": row[0].patientID,
                "DoctorID": row[0].DoctorID,
                "AppointmentDate": row[0].AppointmentDate,
                "AppointmentTime": row[0].AppointmentTime,
                "Complaint": row[0].Complaint,
                "Booked_at": row[0].Booked_at,
                "doctorName": row.doctorName,
                "specialityName": row.specialityName,
                "hospitalName": row.hospitalName,
                "City": row.City,
            }
            for row in results
        ]

    def find_patient_appointment(self, patient_id: int, appointment_id: int, *, lock: bool = False):
        statement = select(Appointments).where(
            Appointments.patientID == patient_id,
            Appointments.AppointmentID == appointment_id,
        )
        if lock:
            statement = statement.with_for_update()
        return self.db.scalar(statement)

    def delete(self, appointment: Appointments) -> None:
        self.db.delete(appointment)

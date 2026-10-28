from typing import TypedDict, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from Doctor.models.DoctorAvailbilityModel import DoctorAvailability
from Doctor.models.DoctorModel import Doctor
from Doctor.models.DoctorSpecialities import Specialities
from Doctor.schemas.DoctorSchemas import DoctorCreate
from Hospital.models.HospitalModel import Hospital


class DoctorCardRow(TypedDict):
    doctorID: int
    Name: str
    YearsofExperience: int
    DailyPatientLimit: int
    specialityID: int
    specialityName: str
    hospitalID: int
    hospitalName: str
    City: str


class DoctorRepository:
    """Database queries used to browse doctors and their filter options."""

    def __init__(self, db: Session):
        self.db = db

    def get_doctor(self, doctor_id: int) -> Doctor | None:
        return self.db.get(Doctor, doctor_id)

    def create_doctor(self, create_request: DoctorCreate) -> Doctor:
        doctor = Doctor(
            name=create_request.name,
            yearsofExperience=create_request.yearsofExperience,
            dailyPatientLimit=create_request.dailyPatientLimit,
            specialtyId=create_request.specialityId,
            hospitalId=create_request.hospitalId,
        )
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def create_availability(self, availability: DoctorAvailability) -> DoctorAvailability:
        self.db.add(availability)
        self.db.commit()
        self.db.refresh(availability)
        return availability

    def search_doctors(
        self,
        search: str | None = None,
        speciality_id: int | None = None,
        city: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[DoctorCardRow]:
        """Return doctor-card fields, applying any provided filters."""
        statement = (
            select(
                Doctor.id.label("doctorID"),
                Doctor.name.label("Name"),
                Doctor.yearsofExperience.label("YearsofExperience"),
                Doctor.dailyPatientLimit.label("DailyPatientLimit"),
                Specialities.id.label("specialityID"),
                Specialities.name.label("specialityName"),
                Hospital.hospitalID.label("hospitalID"),
                Hospital.hospitalName.label("hospitalName"),
                Hospital.City.label("City"),
            )
            .select_from(Doctor)
            .outerjoin(Specialities, Doctor.specialtyId == Specialities.id)
            .outerjoin(Hospital, Doctor.hospitalId == Hospital.hospitalID)
        )

        if search and search.strip():
            term = f"%{search.strip()}%"
            statement = statement.where(
                Doctor.name.ilike(term)
                | Specialities.name.ilike(term)
                | Hospital.hospitalName.ilike(term)
                | Hospital.City.ilike(term)
            )
        if speciality_id is not None:
            statement = statement.where(
                Doctor.specialtyId == speciality_id
            )
        if city and city.strip():
            statement = statement.where(
                func.lower(Hospital.City) == city.strip().lower()
            )

        statement = (
            statement.order_by(func.lower(Doctor.name))
            .limit(limit)
            .offset(offset)
        )
        rows = [dict(row) for row in self.db.execute(statement).mappings().all()]
        doctor_ids = [row["doctorID"] for row in rows]
        if not doctor_ids:
            return []

        timing_statement = (
            select(
                DoctorAvailability.doctorId,
                DoctorAvailability.day,
                DoctorAvailability.startTime,
                DoctorAvailability.endTime,
            )
            .where(
                DoctorAvailability.doctorId.in_(doctor_ids),
                DoctorAvailability.day.is_not(None),
                DoctorAvailability.startTime.is_not(None),
                DoctorAvailability.endTime.is_not(None),
            )
            .order_by(
                DoctorAvailability.doctorId,
                DoctorAvailability.day,
                DoctorAvailability.startTime,
            )
        )
        timings_by_doctor: dict[int, list[dict[str, str]]] = {}
        for timing in self.db.execute(timing_statement).mappings():
            timings_by_doctor.setdefault(timing["doctorId"], []).append(
                {
                    "day": timing["day"],
                    "startTime": timing["startTime"],
                    "endTime": timing["endTime"],
                }
            )

        for row in rows:
            row["timings"] = timings_by_doctor.get(row["doctorID"], [])
        return [cast(DoctorCardRow, row) for row in rows]

    def list_specialities(self) -> list[Specialities]:
        """Return all specialities ordered by name for a filter dropdown."""
        statement = select(Specialities).order_by(
            func.lower(Specialities.name)
        ).where(Specialities.name.is_not(None), func.trim(Specialities.name) != "")
        return list(self.db.scalars(statement).all())

    def list_cities(self) -> list[str]:
        """Return distinct, non-empty hospital cities for a filter dropdown."""
        statement = (
            select(func.min(Hospital.City))
            .where(Hospital.City.is_not(None), func.trim(Hospital.City) != "")
            .group_by(func.lower(func.trim(Hospital.City)))
            .order_by(func.lower(func.min(Hospital.City)))
        )
        return [city for city in self.db.scalars(statement).all() if city is not None]

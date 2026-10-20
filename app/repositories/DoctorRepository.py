
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.DoctorModel import Doctor
from models.DoctorSpecialities import Specialities
from models.HospitalModel import Hospital


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_doctors(
        self,
        search: str | None = None,
        speciality_id: int | None = None,
        city: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return doctor directory rows matching the requested filters."""
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
            statement = statement.where(Doctor.specialtyId == speciality_id)
        if city and city.strip():
            statement = statement.where(
                func.lower(func.trim(Hospital.City)) == city.strip().lower()
            )

        statement = (
            statement.order_by(func.lower(Doctor.name))
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(statement).mappings().all()
        return [dict(row) for row in rows]

        

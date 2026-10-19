
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.DoctorDummyModel import DoctorDummy
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
                DoctorDummy.doctorID.label("doctorID"),
                DoctorDummy.Name.label("Name"),
                DoctorDummy.YearsofExperience.label("YearsofExperience"),
                DoctorDummy.DailyPatientLimit.label("DailyPatientLimit"),
                Specialities.specialityID.label("specialityID"),
                Specialities.specialityName.label("specialityName"),
                Hospital.hospitalID.label("hospitalID"),
                Hospital.hospitalName.label("hospitalName"),
                Hospital.City.label("City"),
            )
            .select_from(DoctorDummy)
            .outerjoin(
                Specialities,
                DoctorDummy.specialityID == Specialities.specialityID,
            )
            .outerjoin(Hospital, DoctorDummy.hospitalID == Hospital.hospitalID)
        )

        if search and search.strip():
            term = f"%{search.strip()}%"
            statement = statement.where(
                DoctorDummy.Name.ilike(term)
                | Specialities.specialityName.ilike(term)
                | Hospital.hospitalName.ilike(term)
            )
        if speciality_id is not None:
            statement = statement.where(DoctorDummy.specialityID == speciality_id)
        if city and city.strip():
            statement = statement.where(
                func.lower(func.trim(Hospital.City)) == city.strip().lower()
            )

        statement = (
            statement.order_by(func.lower(DoctorDummy.Name))
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(statement).mappings().all()
        return [dict(row) for row in rows]

        

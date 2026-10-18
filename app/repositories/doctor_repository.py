from typing import TypedDict, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.DoctorDummyModel import DoctorDummy
from models.DoctorSpecialities import Specialities
from models.HospitalModel import Hospital


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
            .join(
                Specialities,
                DoctorDummy.specialityID == Specialities.specialityID,
            )
            .join(Hospital, DoctorDummy.hospitalID == Hospital.hospitalID)
        )

        if search and search.strip():
            statement = statement.where(
                DoctorDummy.Name.ilike(f"%{search.strip()}%")
            )
        if speciality_id is not None:
            statement = statement.where(
                DoctorDummy.specialityID == speciality_id
            )
        if city and city.strip():
            statement = statement.where(
                func.lower(Hospital.City) == city.strip().lower()
            )

        statement = (
            statement.order_by(func.lower(DoctorDummy.Name))
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(statement).mappings().all()
        return [cast(DoctorCardRow, dict(row)) for row in rows]

    def list_specialities(self) -> list[Specialities]:
        """Return all specialities ordered by name for a filter dropdown."""
        statement = select(Specialities).order_by(
            func.lower(Specialities.specialityName)
        )
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

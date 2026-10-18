from sqlalchemy.orm import Session

from repositories.doctor_repository import DoctorRepository
from schemas.DoctorDirectory import (
    DoctorCardResponse,
    DoctorFilterOptionsResponse,
)
from schemas.DoctorSpecialities import SpecialityRead


class DoctorDirectoryService:
    """Prepare doctor directory results and filter options for the API."""

    def __init__(self, db: Session):
        self.doctors = DoctorRepository(db)

    def list_doctors(
        self,
        *,
        search: str | None = None,
        speciality_id: int | None = None,
        city: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[DoctorCardResponse]:
        rows = self.doctors.search_doctors(
            search=search,
            speciality_id=speciality_id,
            city=city,
            limit=limit,
            offset=offset,
        )
        return [DoctorCardResponse.model_validate(row) for row in rows]

    def get_filter_options(self) -> DoctorFilterOptionsResponse:
        specialities = [
            SpecialityRead.model_validate(item)
            for item in self.doctors.list_specialities()
        ]
        return DoctorFilterOptionsResponse(
            specialities=specialities,
            cities=self.doctors.list_cities(),
        )

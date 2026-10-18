from sqlalchemy.orm import Session

from schemas.DoctorDirectory import (
    DoctorCardResponse,
    DoctorFilterOptionsResponse,
)
from services.doctor_directory import DoctorDirectoryService


def list_doctors_endpoint(
    db: Session,
    *,
    search: str | None = None,
    speciality_id: int | None = None,
    city: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[DoctorCardResponse]:
    return DoctorDirectoryService(db).list_doctors(
        search=search,
        speciality_id=speciality_id,
        city=city,
        limit=limit,
        offset=offset,
    )


def get_doctor_filter_options_endpoint(
    db: Session,
) -> DoctorFilterOptionsResponse:
    return DoctorDirectoryService(db).get_filter_options()

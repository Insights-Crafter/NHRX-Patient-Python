from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers.doctor_controller import (
    get_doctor_filter_options_endpoint,
    list_doctors_endpoint,
)
from database.database import get_db
from schemas.DoctorDirectory import (
    DoctorCardResponse,
    DoctorFilterOptionsResponse,
)


router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorCardResponse])
def list_doctors_route(
    search: str | None = Query(default=None, max_length=120),
    speciality_id: int | None = Query(default=None, gt=0),
    city: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[DoctorCardResponse]:
    return list_doctors_endpoint(
        db,
        search=search,
        speciality_id=speciality_id,
        city=city,
        limit=limit,
        offset=offset,
    )


@router.get("/filters", response_model=DoctorFilterOptionsResponse)
def doctor_filter_options_route(
    db: Session = Depends(get_db),
) -> DoctorFilterOptionsResponse:
    return get_doctor_filter_options_endpoint(db)

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.database import get_db
from Doctor.schemas.DoctorSchemas import (
    DoctorCardResponse,
    DoctorFilterOptionsResponse,
    DoctorCreate,
    DoctorAvailabilityCreate,
    DoctorAvailabilityRead,
)
from Doctor.services.doctor_directory import DoctorDirectoryService


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
    return DoctorDirectoryService(db).list_doctors(
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
    return DoctorDirectoryService(db).get_filter_options()


@router.post("/doctor")
def createdoctor(
    createRequest: DoctorCreate,
    db: Session = Depends(get_db),
):
    return DoctorDirectoryService(db).createDoctor(createRequest=createRequest)


@router.post(
    "/availability",
    response_model=DoctorAvailabilityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor_availability(
    request: DoctorAvailabilityCreate,
    db: Session = Depends(get_db),
) -> DoctorAvailabilityRead:
    """Add one recurring weekly availability slot for a doctor."""
    return DoctorDirectoryService(db).create_availability(request)


    

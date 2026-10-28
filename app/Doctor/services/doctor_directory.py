from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from Doctor.repositories.doctor_repository import DoctorRepository
from Doctor.models.DoctorAvailbilityModel import DoctorAvailability
from Doctor.schemas.DoctorSchemas import (
    DoctorCardResponse,
    DoctorFilterOptionsResponse,
    SpecialityRead,
    DoctorCreate,
    DoctorAvailabilityCreate,
    DoctorAvailabilityRead,
)

from Doctor.models.DoctorModel import Doctor


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
            SpecialityRead(
                specialityID=item.id,
                specialityName=item.name,
            )
            for item in self.doctors.list_specialities()
        ]
        return DoctorFilterOptionsResponse(
            specialities=specialities,
            cities=self.doctors.list_cities(),
        )

    def createDoctor(self, createRequest: DoctorCreate):
        return self.doctors.create_doctor(createRequest)

    def create_availability(
        self, request: DoctorAvailabilityCreate
    ) -> DoctorAvailabilityRead:
        if self.doctors.get_doctor(request.doctorId) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )

        availability = DoctorAvailability(
            doctorId=request.doctorId,
            day=request.day,
            startTime=request.startTime,
            endTime=request.endTime,
        )
        created = self.doctors.create_availability(availability)
        return DoctorAvailabilityRead.model_validate(created)
        
        



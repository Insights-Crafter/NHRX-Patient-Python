from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from Hospital.schemas.Hospital import (
    HospitalCreate,
    HospitalCreateResponse,
    HospitalNameUpdate,
    HospitalNameUpdateResponse,
)
from Hospital.services.hospital_service import create_hospital, rename_hospital


routerHospital = APIRouter(prefix="/hospital", tags=['Hospital'])


@routerHospital.patch("/updateName")
def update_hospital_name(
    request: HospitalNameUpdate,
    db: Session = Depends(get_db),
) -> HospitalNameUpdateResponse:
    return rename_hospital(request, db)


@routerHospital.post(
    "/create",
    response_model=HospitalCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hospital_route(request: HospitalCreate, db: Session = Depends(get_db)):
    
    return create_hospital(request, db)

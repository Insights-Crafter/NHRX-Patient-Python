from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.PatientModel import (
    PatientRegistrationRequest,
    PatientRegistrationResponse,
)
from services.patient_registration import register_patient

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "/register",
    response_model=PatientRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_patient_endpoint(
    registration: PatientRegistrationRequest,
    db: Session = Depends(get_db),
) -> PatientRegistrationResponse:
    patient_id = register_patient(db, registration)
    return PatientRegistrationResponse(patientID=patient_id)


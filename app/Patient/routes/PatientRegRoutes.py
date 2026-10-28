from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.database import get_db
from Patient.schemas.PatientModel import PatientRegistrationRequest, PatientRegistrationResponse
from Patient.services.patient_registration import PatientRegistrationService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "/register",
    response_model=PatientRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_patient_route(
    registration: PatientRegistrationRequest,
    db: Session = Depends(get_db),
) -> PatientRegistrationResponse:
    patient_id = PatientRegistrationService(db).register(registration)
    return PatientRegistrationResponse(patientID=patient_id)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from controllers.patient_controller import register_patient_endpoint
from database.database import get_db
from schemas.PatientModel import PatientRegistrationRequest, PatientRegistrationResponse

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
    return register_patient_endpoint(registration, db)

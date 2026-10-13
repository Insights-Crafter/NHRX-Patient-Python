from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ReusableFunctions import ExtractPatientID
from database.database import get_db
from schemas.PatientModel import (
    PatientRegistrationRequest,
    PatientRegistrationResponse,
)
from services.patient_registration import register_patient
from repositories.patient_repository import get_patient_by_id
from JWT.jwt_handler import verify_access_token
from utilityfunctions.encryption import decrypt

router = APIRouter(prefix="/patients", tags=["patients"])
bearer_scheme = HTTPBearer(auto_error=False)





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



@router.get("/me")
def get_current_patient(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict[str, str | int | None]:

    patient_id = ExtractPatientID(credentials)

    patient = get_patient_by_id(db, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return {
        "patientID": patient.patientID,
        "firstName": decrypt(patient.firstName, "firstName"),
        "lastName": decrypt(patient.lastName, "lastName"),
    }

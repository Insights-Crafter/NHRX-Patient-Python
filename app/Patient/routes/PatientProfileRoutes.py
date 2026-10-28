from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.database import get_db
from Patient.repositories.patient_repository import PatientRepository
from utilityfunctions.encryption import EncryptionService
from utilityfunctions.reusable_functions import extract_patient_id

router = APIRouter(prefix="/patients", tags=["patients"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/me")
def get_current_patient_route(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict[str, str | int | None]:
    patient_id = extract_patient_id(credentials)
    patient = PatientRepository(db).get_by_id(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    encryption = EncryptionService()
    return {
        "patientID": patient.patientID,
        "firstName": encryption.decrypt(patient.firstName, "firstName"),
        "lastName": encryption.decrypt(patient.lastName, "lastName"),
    }

"""Authentication workflow for patient credentials."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from Patient.repositories.patient_repository import PatientRepository
from utilityfunctions.encryption import EncryptionService
from utilityfunctions.passwords import verify_password


class AuthenticationService:
    
    def __init__(self, db: Session):
        self.patients = PatientRepository(db)
        self.encryption = EncryptionService()

    def authenticate(self, national_id: str, password: str) -> int:
        encrypted_national_id = self.encryption.encrypt(
            national_id.strip(), "nationalID"
        )
        credentials = self.patients.get_user_credentials(encrypted_national_id)

        if credentials is None or not verify_password(password, credentials[0]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid national ID or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials[1]

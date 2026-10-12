"""Authentication service: coordinate lookup and credential verification."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.patient_repository import get_user_credentials
from utilityfunctions.encryption import encrypt
from utilityfunctions.passwords import verify_password


def authenticate_patient(db: Session, national_id: str, password: str) -> int:
    """Return the patient's internal ID for valid credentials."""
    encrypted_national_id = encrypt(national_id.strip(), "nationalID")
    credentials = get_user_credentials(db, encrypted_national_id)

    if credentials is None or not verify_password(password, credentials[0]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid national ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials[1]

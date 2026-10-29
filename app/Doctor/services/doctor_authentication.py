"""Authenticate doctors using their configured password credentials."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from Doctor.repositories.doctor_repository import DoctorRepository
from utilityfunctions.passwords import verify_password


class DoctorAuthenticationService:
    def __init__(self, db: Session):
        self.doctors = DoctorRepository(db)

    def authenticate(self, doctor_id: int, password: str) -> int:
        credentials = self.doctors.get_doctor_authentication(doctor_id)
        if credentials is None or not verify_password(
            password, credentials.passwordHash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid doctor ID or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials.doctorId

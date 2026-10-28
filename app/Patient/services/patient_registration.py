from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from Patient.repositories.patient_repository import PatientRepository
from Patient.schemas.PatientModel import PatientRegistrationRequest
from utilityfunctions.encryption import EncryptionService
from utilityfunctions.passwords import hash_password


class PatientRegistrationService:
  
    def __init__(self, db: Session):
        self.db = db
        self.patients = PatientRepository(db)
        self.encryption = EncryptionService()

    def register(self, registration: PatientRegistrationRequest) -> int:
        encrypted_national_id = self.encryption.encrypt(
            registration.nationalID.strip(), "nationalID"
        )

        if self.patients.get_by_national_id(encrypted_national_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A patient with this national ID is already registered",
            )

        patient_fields = {
            "firstName": self.encryption.encrypt(
                registration.firstName.strip(), "firstName"
            ),
            "lastName": self.encryption.encrypt(
                registration.lastName.strip(), "lastName"
            ),
            "date_of_birth": self.encryption.encrypt(
                registration.date_of_birth.isoformat()
                if registration.date_of_birth
                else None,
                "date_of_birth",
            ),
            "blood_group": self.encryption.encrypt(
                registration.blood_group, "blood_group"
            ),
            "gender": self.encryption.encrypt(registration.gender, "gender"),
            "phone": self.encryption.encrypt(registration.phone, "phone"),
            "email": self.encryption.encrypt(registration.email, "email"),
        }

        try:
            patient = self.patients.create_with_credentials(
                patient_fields=patient_fields,
                encrypted_national_id=encrypted_national_id,
                password_hash=hash_password(registration.password),
            )
            if registration.address is not None:
                address_fields = {
                    field: self.encryption.encrypt(value.strip(), field)
                    for field, value in registration.address.model_dump().items()
                }
                self.patients.create_address(patient.patientID, address_fields)
            self.db.commit()
            self.db.refresh(patient)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A patient with this national ID is already registered",
            ) from exc
        return patient.patientID

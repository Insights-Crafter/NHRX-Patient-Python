from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from Patient.repositories.patient_repository import PatientRepository
from Patient.schemas.ContactUpdate import ContactUpdateRequest, ContactUpdateResponse
from utilityfunctions.encryption import EncryptionService


class PatientContactService:
    """Update and decrypt the patient's contact information."""

    def __init__(self, db: Session):
        self.patients = PatientRepository(db)
        self.encryption = EncryptionService()

    def update(
        self, patient_id: int, request: ContactUpdateRequest
    ) -> ContactUpdateResponse:
        supplied_fields = request.model_dump(exclude_unset=True)
        if not supplied_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provide at least one contact field to update",
            )

        encrypted_fields = {
            field: self.encryption.encrypt(value, field)
            for field, value in supplied_fields.items()
        }
        patient = self.patients.update_contact(encrypted_fields, patient_id)
        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        return ContactUpdateResponse(
            email=self.encryption.decrypt(patient.email, "email"),
            phone=self.encryption.decrypt(patient.phone, "phone"),
        )

    def get(self, patient_id: int) -> ContactUpdateResponse:
        patient = self.patients.get_by_id(patient_id)
        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )
        return ContactUpdateResponse(
            email=self.encryption.decrypt(patient.email, "email"),
            phone=self.encryption.decrypt(patient.phone, "phone"),
        )

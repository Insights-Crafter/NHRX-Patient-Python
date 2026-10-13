from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.patient_repository import update_contact
from schemas.ContactUpdate import ContactUpdateRequest, ContactUpdateResponse
from utilityfunctions.encryption import decrypt, encrypt


def update_patient_contact(
    db: Session, patient_id: int, request: ContactUpdateRequest
) -> ContactUpdateResponse:
    supplied_fields = request.model_dump(exclude_unset=True)
    if not supplied_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one contact field to update",
        )

    encrypted_fields = {
        field: encrypt(value, field) for field, value in supplied_fields.items()
    }
    patient = update_contact(db, encrypted_fields, patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return ContactUpdateResponse(
        email=decrypt(patient.email, "email"),
        phone=decrypt(patient.phone, "phone"),
    )

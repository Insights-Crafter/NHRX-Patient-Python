from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from repositories.patient_repository import (
    create_patient_with_credentials,
    get_patient_by_national_id,
)
from schemas.PatientModel import PatientRegistrationRequest
from utilityfunctions.encryption import encrypt
from utilityfunctions.passwords import hash_password


def register_patient(
    db: Session, registration: PatientRegistrationRequest
) -> int:
    """Validate uniqueness, protect patient data, and create the account."""
    
    encrypted_national_id = encrypt(registration.nationalID.strip(), "nationalID")

    if get_patient_by_national_id(db, encrypted_national_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A patient with this national ID is already registered",
        )

    patient_fields = {
        "firstName": encrypt(registration.firstName.strip(), "firstName"),
        "lastName": encrypt(registration.lastName.strip(), "lastName"),
        "date_of_birth": encrypt(
            registration.date_of_birth.isoformat() if registration.date_of_birth else None,
            "date_of_birth",
        ),
        "blood_group": encrypt(registration.blood_group, "blood_group"),
        "gender": encrypt(registration.gender, "gender"),
        "phone": encrypt(registration.phone, "phone"),
        "email": encrypt(registration.email, "email"),
    }

    try:
        patient = create_patient_with_credentials(
            db,
            patient_fields=patient_fields,
            encrypted_national_id=encrypted_national_id,
            password_hash=hash_password(registration.password),
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A patient with this national ID is already registered",
        ) from exc
    return patient.patientID

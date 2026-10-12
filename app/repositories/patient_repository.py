from datetime import datetime

from sqlalchemy.orm import Session

from models.AuthCredModel import AuthCredentials
from models.PatientModel import Patient


def get_patient_by_national_id(db: Session, encrypted_national_id: str) -> Patient | None:
    return (
        db.query(Patient)
        .filter(Patient.nationalID == encrypted_national_id)
        .first()
    )


def create_patient_with_credentials(
    db: Session,
    *,
    patient_fields: dict[str, object],
    encrypted_national_id: str,
    password_hash: str,
) -> Patient:
    """Persist a patient and login credential as one database transaction."""
    patient = Patient(
        **patient_fields,
        nationalID=encrypted_national_id,
        createdAt=datetime.now(),
    )
    db.add(patient)
    db.flush()

    credential = AuthCredentials(
        patientID=patient.patientID,
        nationalID=encrypted_national_id,
        password=password_hash,
    )
    db.add(credential)
    db.commit()
    db.refresh(patient)
    return patient

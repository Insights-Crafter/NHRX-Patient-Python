from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from models.AuthCredModel import AuthCredentials
from models.PatientModel import Patient
from models.AuthCredModel import AuthCredentials


def get_patient_by_national_id(db: Session, encrypted_national_id: str) -> Patient | None:
    return (
        db.query(Patient)
        .filter(Patient.nationalID == encrypted_national_id)
        .first()
    )


def get_patient_by_id(db: Session, patient_id: int) -> Patient | None:
    return db.query(Patient).filter(Patient.patientID == patient_id).first()


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


def get_user_credentials(
    db: Session, encrypted_national_id: str
) -> tuple[str, int] | None:
    query = select(AuthCredentials.password, Patient.patientID).join(Patient,
        Patient.patientID == AuthCredentials.patientID
    ).where(Patient.nationalID == encrypted_national_id)
    row = db.execute(query).one_or_none()
    return (row[0], row[1]) if row is not None else None
    
    


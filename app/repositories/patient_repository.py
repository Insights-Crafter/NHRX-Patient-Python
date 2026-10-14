from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from models.AuthCredModel import AuthCredentials
from models.PatientModel import Patient
from models.PatientAddress import PatientAddress


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
    return patient


def create_patient_address(
    db: Session, patient_id: int, encrypted_address_fields: dict[str, str | None]
) -> PatientAddress:
    """Add an address row linked to an already-flushed patient."""
    address = PatientAddress(patientID=patient_id, **encrypted_address_fields)
    db.add(address)
    db.flush()
    return address


def get_user_credentials(
    db: Session, encrypted_national_id: str
) -> tuple[str, int] | None:
    query = (
        select(AuthCredentials.password, Patient.patientID)
        .join(Patient, Patient.patientID == AuthCredentials.patientID)
        .where(Patient.nationalID == encrypted_national_id)
    )
    row = db.execute(query).one_or_none()
    return (row[0], row[1]) if row is not None else None


def update_address(
    db: Session, patient_id: int, address_fields: dict[str, str | None]
) -> PatientAddress | None:
    """Update the patient's first address row and return it, or None if absent."""
    address = db.execute(
        select(PatientAddress)
        .where(PatientAddress.patientID == patient_id)
        .order_by(PatientAddress.AddressID)
        .limit(1)
    ).scalar_one_or_none()

    if address is None:
        return None

    result = db.execute(
        update(PatientAddress)
        .where(PatientAddress.AddressID == address.AddressID)
        .values(**address_fields)
    )
    if result.rowcount == 0:
        db.rollback()
        return None

    db.commit()
    db.refresh(address)
    return address


def get_patient_address(db: Session, patient_id: int) -> PatientAddress | None:
    """Return the patient's first address row, or None if it is absent."""
    return db.execute(
        select(PatientAddress)
        .where(PatientAddress.patientID == patient_id)
        .order_by(PatientAddress.AddressID)
        .limit(1)
    ).scalar_one_or_none()

def update_contact(
    db: Session,
    encrypted_fields: dict[str, str | None],
    patient_id: int,
) -> Patient | None:
    """Update a patient's encrypted contact fields and return the patient."""
    patient = db.execute(
        select(Patient).where(Patient.patientID == patient_id)
    ).scalar_one_or_none()
    if patient is None:
        return None

    try:
        result = db.execute(
            update(Patient)
            .where(Patient.patientID == patient_id)
            .values(**encrypted_fields)
        )
        if result.rowcount == 0:
            db.rollback()
            return None

        db.commit()
        db.refresh(patient)
        return patient
    except Exception:
        db.rollback()
        raise


def getPatientAddress(db:Session, patientID:int):
    result = db.execute(select(PatientAddress.Area,PatientAddress.Block,
                                PatientAddress.City,
                                PatientAddress.Province, PatientAddress.Street,
                                PatientAddress.HouseNumber).where(PatientAddress.patientID==patientID))
    address = result.mappings().one_or_none()
    return dict(address) if address is not None else None

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.AuthCredModel import AuthCredentials
from models.PatientAddress import PatientAddress
from models.PatientModel import Patient


class PatientRepository:
    """Database operations for patients and their related records."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_national_id(self, encrypted_national_id: str) -> Patient | None:
        return (
            self.db.query(Patient)
            .filter(Patient.nationalID == encrypted_national_id)
            .first()
        )

    def get_by_id(self, patient_id: int) -> Patient | None:
        return self.db.query(Patient).filter(Patient.patientID == patient_id).first()

    def create_with_credentials(
        self,
        *,
        patient_fields: dict[str, object],
        encrypted_national_id: str,
        password_hash: str,
    ) -> Patient:
        """Stage a patient and credential in the current transaction."""
        patient = Patient(
            **patient_fields,
            nationalID=encrypted_national_id,
            createdAt=datetime.now(),
        )
        self.db.add(patient)
        self.db.flush()

        credential = AuthCredentials(
            patientID=patient.patientID,
            nationalID=encrypted_national_id,
            password=password_hash,
        )
        self.db.add(credential)
        return patient

    def create_address(
        self, patient_id: int, encrypted_address_fields: dict[str, str | None]
    ) -> PatientAddress:
        """Stage an address linked to an already-flushed patient."""
        address = PatientAddress(patientID=patient_id, **encrypted_address_fields)
        self.db.add(address)
        self.db.flush()
        return address

    def get_user_credentials(
        self, encrypted_national_id: str
    ) -> tuple[str, int] | None:
        query = (
            select(AuthCredentials.password, Patient.patientID)
            .join(Patient, Patient.patientID == AuthCredentials.patientID)
            .where(Patient.nationalID == encrypted_national_id)
        )
        row = self.db.execute(query).one_or_none()
        return (row[0], row[1]) if row is not None else None

    def update_address(
        self, patient_id: int, address_fields: dict[str, str | None]
    ) -> PatientAddress | None:
        """Update the patient's first address row and return it, or None if absent."""
        address = self.db.execute(
            select(PatientAddress)
            .where(PatientAddress.patientID == patient_id)
            .order_by(PatientAddress.AddressID)
            .limit(1)
        ).scalar_one_or_none()

        if address is None:
            return None

        result = self.db.execute(
            update(PatientAddress)
            .where(PatientAddress.AddressID == address.AddressID)
            .values(**address_fields)
        )
        if result.rowcount == 0:
            self.db.rollback()
            return None

        self.db.commit()
        self.db.refresh(address)
        return address

    def get_address(self, patient_id: int) -> PatientAddress | None:
        """Return the patient's first address row, or None if it is absent."""
        return self.db.execute(
            select(PatientAddress)
            .where(PatientAddress.patientID == patient_id)
            .order_by(PatientAddress.AddressID)
            .limit(1)
        ).scalar_one_or_none()

    def update_contact(
        self, encrypted_fields: dict[str, str | None], patient_id: int
    ) -> Patient | None:
        """Update a patient's encrypted contact fields and return the patient."""
        patient = self.db.execute(
            select(Patient).where(Patient.patientID == patient_id)
        ).scalar_one_or_none()
        if patient is None:
            return None

        try:
            result = self.db.execute(
                update(Patient)
                .where(Patient.patientID == patient_id)
                .values(**encrypted_fields)
            )
            if result.rowcount == 0:
                self.db.rollback()
                return None

            self.db.commit()
            self.db.refresh(patient)
            return patient
        except Exception:
            self.db.rollback()
            raise

    def get_patient_address_fields(self, patient_id: int):
        result = self.db.execute(
            select(
                PatientAddress.Area,
                PatientAddress.Block,
                PatientAddress.City,
                PatientAddress.Province,
                PatientAddress.Street,
                PatientAddress.HouseNumber,
            ).where(PatientAddress.patientID == patient_id)
        )
        address = result.mappings().one_or_none()
        return dict(address) if address is not None else None



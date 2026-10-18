from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from repositories.patient_repository import PatientRepository
from schemas.AddressUpdate import AddressUpdateRequest, AddressUpdateResponse
from schemas.PatientModel import PatientRegistrationRequest, PatientRegistrationResponse
from services.patient_address import PatientAddressService
from services.patient_registration import PatientRegistrationService
from utilityfunctions.encryption import EncryptionService
from utilityfunctions.reusable_functions import extract_patient_id

from schemas.ContactUpdate import ContactUpdateRequest, ContactUpdateResponse
from services.patient_contact import PatientContactService


def register_patient_endpoint(
    registration: PatientRegistrationRequest, db: Session
) -> PatientRegistrationResponse:
    patient_id = PatientRegistrationService(db).register(registration)
    return PatientRegistrationResponse(patientID=patient_id)


def get_current_patient(
    credentials: HTTPAuthorizationCredentials | None, db: Session
) -> dict[str, str | int | None]:
    patient_id = extract_patient_id(credentials)
    patient = PatientRepository(db).get_by_id(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    encryption = EncryptionService()
    return {
        "patientID": patient.patientID,
        "firstName": encryption.decrypt(patient.firstName, "firstName"),
        "lastName": encryption.decrypt(patient.lastName, "lastName"),
    }


def update_current_patient_address(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
    request: AddressUpdateRequest,
) -> AddressUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return PatientAddressService(db).update(patient_id, request)


def get_current_patient_address(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> AddressUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return PatientAddressService(db).get(patient_id)


def update_current_patient_contact(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
    request: ContactUpdateRequest,
) -> ContactUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return PatientContactService(db).update(patient_id, request)


def get_current_patient_contact(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> ContactUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return PatientContactService(db).get(patient_id)


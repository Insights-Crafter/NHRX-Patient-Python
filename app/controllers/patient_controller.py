from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from repositories.patient_repository import get_patient_by_id
from schemas.AddressUpdate import AddressUpdateRequest, AddressUpdateResponse
from schemas.PatientModel import PatientRegistrationRequest, PatientRegistrationResponse
from services.patient_address import update_patient_address
from services.patient_registration import register_patient
from utilityfunctions.encryption import decrypt
from utilityfunctions.reusable_functions import extract_patient_id

from schemas.ContactUpdate import ContactUpdateRequest, ContactUpdateResponse
from services.patient_contact import update_patient_contact


def register_patient_endpoint(
    registration: PatientRegistrationRequest, db: Session
) -> PatientRegistrationResponse:
    patient_id = register_patient(db, registration)
    return PatientRegistrationResponse(patientID=patient_id)


def get_current_patient(
    credentials: HTTPAuthorizationCredentials | None, db: Session
) -> dict[str, str | int | None]:
    patient_id = extract_patient_id(credentials)
    patient = get_patient_by_id(db, patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return {
        "patientID": patient.patientID,
        "firstName": decrypt(patient.firstName, "firstName"),
        "lastName": decrypt(patient.lastName, "lastName"),
    }


def update_current_patient_address(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
    request: AddressUpdateRequest,
) -> AddressUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return update_patient_address(db, patient_id, request)

def update_current_patient_contact(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
    request: ContactUpdateRequest,
) -> ContactUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return update_patient_contact(db, patient_id, request)


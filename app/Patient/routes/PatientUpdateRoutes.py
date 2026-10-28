from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.database import get_db
from Patient.schemas.AddressUpdate import (
    AddressUpdateRequest,
    AddressUpdateResponse,
    UserAddressUpdateResponse,
)
from Patient.services.patient_address import PatientAddressService
from Patient.services.patient_contact import PatientContactService
from utilityfunctions.reusable_functions import extract_patient_id
from Patient.schemas.ContactUpdate import (
    ContactUpdateRequest,
    ContactUpdateResponse,
    UserContactUpdateResponse,
)

bearer_scheme = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me/address", response_model=AddressUpdateResponse)
def get_address_route(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AddressUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return PatientAddressService(db).get(patient_id)


@router.patch("/me/address", response_model=UserAddressUpdateResponse)
@router.patch("/me/updateAdress", response_model=UserAddressUpdateResponse, include_in_schema=False)
def update_address_route(
    request: AddressUpdateRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserAddressUpdateResponse:
    patient_id = extract_patient_id(credentials)
    address = PatientAddressService(db).update(patient_id, request)
    return UserAddressUpdateResponse(
        message="Patient address updated successfully",
        data=address,
    )


@router.patch("/me/contact", response_model=UserContactUpdateResponse)
@router.patch("/me/updateContact", response_model=UserContactUpdateResponse, include_in_schema=False)
def update_contact_route(
    request: ContactUpdateRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserContactUpdateResponse:
    patient_id = extract_patient_id(credentials)
    contact = PatientContactService(db).update(patient_id, request)
    return UserContactUpdateResponse(
        message="Patient contact information updated successfully",
        data=contact,
    )


@router.get("/me/contact", response_model=ContactUpdateResponse)
def get_contact_route(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> ContactUpdateResponse:
    patient_id = extract_patient_id(credentials)
    return PatientContactService(db).get(patient_id)

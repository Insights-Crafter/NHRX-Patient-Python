from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from controllers.patient_controller import (
    get_current_patient_address,
    get_current_patient_contact,
    update_current_patient_address,
    update_current_patient_contact,
)
from database.database import get_db
from schemas.AddressUpdate import (
    AddressUpdateRequest,
    AddressUpdateResponse,
    UserAddressUpdateResponse,
)
from schemas.ContactUpdate import (
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
    return get_current_patient_address(credentials, db)


@router.patch("/me/address", response_model=UserAddressUpdateResponse)
@router.patch("/me/updateAdress", response_model=UserAddressUpdateResponse, include_in_schema=False)
def update_address_route(
    request: AddressUpdateRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserAddressUpdateResponse:
    address = update_current_patient_address(credentials, db, request)
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
    contact = update_current_patient_contact(credentials, db, request)
    return UserContactUpdateResponse(
        message="Patient contact information updated successfully",
        data=contact,
    )


@router.get("/me/contact", response_model=ContactUpdateResponse)
def get_contact_route(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> ContactUpdateResponse:
    return get_current_patient_contact(credentials, db)

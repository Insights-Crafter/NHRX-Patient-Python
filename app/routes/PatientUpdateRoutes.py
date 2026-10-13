from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from controllers.patient_controller import update_current_patient_address
from database.database import get_db
from schemas.AddressUpdate import AddressUpdateRequest, UserAddressUpdateResponse

bearer_scheme = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/patients", tags=["patients"])


@router.patch("/me/updateAdress", response_model=UserAddressUpdateResponse)
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

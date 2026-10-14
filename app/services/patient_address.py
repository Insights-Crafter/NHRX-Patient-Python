from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.patient_repository import (
    create_patient_address,
    get_patient_address as load_patient_address,
    update_address,
)
from schemas.AddressUpdate import AddressUpdateRequest, AddressUpdateResponse
from utilityfunctions.encryption import decrypt, encrypt


def update_patient_address(
    db: Session,
    patient_id: int,
    request: AddressUpdateRequest,
) -> AddressUpdateResponse:

    supplied_fields = request.model_dump(exclude_unset=True)

    if not supplied_fields:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one address field to update",
        )

    encrypted_fields = {}

    for field, value in supplied_fields.items():
        encrypted_fields[field] = encrypt(value, field)

    existing_address = load_patient_address(db, patient_id)
    if existing_address is None:
        address = create_patient_address(db, patient_id, encrypted_fields)
        db.commit()
        db.refresh(address)
    else:
        address = update_address(db, patient_id, encrypted_fields)

    if address is None:
        raise HTTPException(
            status_code=404,
            detail="Patient address not found",
        )

    return AddressUpdateResponse(
        area=decrypt(address.Area, "Area"),
        houseNo=decrypt(address.HouseNumber, "HouseNumber"),
        province=decrypt(address.Province, "Province"),
        city=decrypt(address.City, "City"),
        street=decrypt(address.Street, "Street"),
        block=decrypt(address.Block, "Block"),
    )


def get_patientt_address(db: Session, patient_id: int) -> AddressUpdateResponse:
    """Load and decrypt the patient's address for an API response."""
    address = load_patient_address(db, patient_id)

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient address not found",
        )

    return AddressUpdateResponse(
        area=decrypt(address.Area, "Area"),
        houseNo=decrypt(address.HouseNumber, "HouseNumber"),
        province=decrypt(address.Province, "Province"),
        city=decrypt(address.City, "City"),
        street=decrypt(address.Street, "Street"),
        block=decrypt(address.Block, "Block"),
    )

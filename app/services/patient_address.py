from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.patient_repository import update_address
from schemas.AddressUpdate import AddressUpdateRequest, AddressUpdateResponse
from utilityfunctions.encryption import decrypt, encrypt


ADDRESS_FIELDS = {
    "Area": "area",
    "HouseNumber": "houseNo",
    "Province": "province",
    "City": "city",
    "Street": "street",
    "Block": "block",
}


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

    address = update_address(db, patient_id, encrypted_fields)

    if address is None:
        raise HTTPException(
            status_code=404,
            detail="Patient address not found",
        )

    return AddressUpdateResponse(
        area=decrypt(address.area, "area"),
        houseNo=decrypt(address.houseNo, "houseNo"),
        province=decrypt(address.province, "province"),
        city=decrypt(address.city, "city"),
        street=decrypt(address.street, "street"),
        block=decrypt(address.block, "block"),
    )
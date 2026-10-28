from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from Patient.models.PatientAddress import PatientAddress
from Patient.repositories.patient_repository import PatientRepository
from Patient.schemas.AddressUpdate import AddressUpdateRequest, AddressUpdateResponse
from utilityfunctions.encryption import EncryptionService


class PatientAddressService:
    """Read and update patient addresses through the repository."""

    def __init__(self, db: Session):
        self.db = db
        self.patients = PatientRepository(db)
        self.encryption = EncryptionService()

    def update(
        self, patient_id: int, request: AddressUpdateRequest
    ) -> AddressUpdateResponse:
        supplied_fields = request.model_dump(exclude_unset=True)
        if not supplied_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provide at least one address field to update",
            )

        encrypted_fields = {
            field: self.encryption.encrypt(value, field)
            for field, value in supplied_fields.items()
        }
        address = self.patients.get_address(patient_id)
        if address is None:
            address = self.patients.create_address(patient_id, encrypted_fields)
            self.db.commit()
            self.db.refresh(address)
        else:
            address = self.patients.update_address(patient_id, encrypted_fields)

        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient address not found",
            )
        return self._to_response(address)

    def get(self, patient_id: int) -> AddressUpdateResponse:
        address = self.patients.get_address(patient_id)
        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient address not found",
            )
        return self._to_response(address)

    def _to_response(self, address: PatientAddress) -> AddressUpdateResponse:
        """Decrypt an ORM address into the API response schema."""
        return AddressUpdateResponse(
            area=self.encryption.decrypt(address.Area, "Area"),
            houseNo=self.encryption.decrypt(address.HouseNumber, "HouseNumber"),
            province=self.encryption.decrypt(address.Province, "Province"),
            city=self.encryption.decrypt(address.City, "City"),
            street=self.encryption.decrypt(address.Street, "Street"),
            block=self.encryption.decrypt(address.Block, "Block"),
        )

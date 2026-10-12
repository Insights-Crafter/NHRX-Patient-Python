from pydantic import BaseModel, ConfigDict


class PatientAddressCreate(BaseModel):
    patientID: int | None = None
    Area: str | None = None
    HouseNumber: str | None = None
    Province: str | None = None
    City: str | None = None
    Street: str | None = None
    Block: str | None = None


class PatientAddressRead(PatientAddressCreate):
    model_config = ConfigDict(from_attributes=True)

    AddressID: int

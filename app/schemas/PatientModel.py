from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientAddressRegistration(BaseModel):
    Area: str = Field(min_length=1, max_length=200)
    HouseNumber: str = Field(min_length=1, max_length=100)
    Province: str = Field(min_length=1, max_length=100)
    City: str = Field(min_length=1, max_length=100)
    Street: str = Field(min_length=1, max_length=200)
    Block: str = Field(min_length=1, max_length=100)

    @field_validator("Area", "HouseNumber", "Province", "City", "Street", "Block")
    @classmethod
    def address_fields_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Address fields must not be blank")
        return value


class PatientCreate(BaseModel):
    nationalID: str  = Field(min_length=11, max_length=11)
    firstName: str | None = None
    lastName: str | None = None
    date_of_birth: str | None = None
    blood_group: str | None = None
    gender: str | None = None
    phone: str  = Field(min_length=11, max_length=11)
    email: str | None = None
    createdAt: date | None = None


class PatientRead(PatientCreate):
    model_config = ConfigDict(from_attributes=True)

    patientID: int


class PatientRegistrationRequest(BaseModel):
    nationalID: str = Field(min_length=13, max_length=13)
    firstName: str = Field(min_length=1, max_length=100)
    lastName: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    date_of_birth: date | None = None
    blood_group: str = Field(min_length=2, max_length=4)
    gender: str  = Field(min_length=3, max_length=32)
    phone: str = Field(min_length=11, max_length=32)
    email: str | None = Field(default=None, max_length=254)
    address: PatientAddressRegistration | None = None

    @field_validator("nationalID", "firstName", "lastName")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank")
        return value


class PatientRegistrationResponse(BaseModel):
    patientID: int
    message: str = "Patient registered successfully"

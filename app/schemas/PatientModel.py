from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientCreate(BaseModel):
    nationalID: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    date_of_birth: str | None = None
    blood_group: str | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    createdAt: date | None = None


class PatientRead(PatientCreate):
    model_config = ConfigDict(from_attributes=True)

    patientID: int


class PatientRegistrationRequest(BaseModel):
    nationalID: str = Field(min_length=1, max_length=64)
    firstName: str = Field(min_length=1, max_length=100)
    lastName: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    date_of_birth: date | None = None
    blood_group: str = Field(min_length=2, max_length=4)
    gender: str  = Field(min_length=3, max_length=32)
    phone: str = Field(min_length=11, max_length=32)
    email: str | None = Field(default=None, max_length=254)

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

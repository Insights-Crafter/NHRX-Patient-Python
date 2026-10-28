"""Pydantic schemas for hospital requests and responses."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HospitalCreate(BaseModel):
    hospitalName: str = Field(min_length=1, max_length=150)
    City: str = Field(min_length=1, max_length=100)

    @field_validator("hospitalName", "City")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank")
        return value

    @field_validator("hospitalName")
    @classmethod
    def title_case_hospital_name(cls, value: str) -> str:
        return value.title()


class HospitalCreateResponse(BaseModel):
    hospitalID: int
    hospitalName: str
    City: str
    message: str = "Hospital created successfully"


class HospitalRead(HospitalCreate):
    model_config = ConfigDict(from_attributes=True)

    hospitalID: int


class HospitalNameUpdate(BaseModel):
    hospitalID: int = Field(gt=0)
    hospitalName: str = Field(min_length=1, max_length=150)

    @field_validator("hospitalName")
    @classmethod
    def check_new_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Hospital name must not be blank")
        return value.title()


class HospitalNameUpdateResponse(BaseModel):
    oldName: str
    newName: str
    message: str = "Hospital name updated successfully"

"""Pydantic schemas for doctor, speciality, and availability data."""

from datetime import time
from typing import Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


Weekday = Literal[
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class DoctorCreate(BaseModel):
    """Input required to create a doctor row."""

    name: str = Field(min_length=1, max_length=120)
    yearsofExperience: int = Field(ge=0)
    dailyPatientLimit: int = Field(gt=0)
    specialityId: int = Field(gt=0)
    hospitalId: int = Field(gt=0)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Doctor name must not be blank")
        return value

    @field_validator("name")
    @classmethod
    def title_case_name(cls, value: str) -> str:
        return value.title()


class DoctorRead(BaseModel):
    """Doctor data returned from its ORM model."""

    model_config = ConfigDict(from_attributes=True)

    doctorID: int = Field(validation_alias="id")
    Name: str | None = Field(validation_alias="name")
    YearsofExperience: int | None = Field(validation_alias="yearsofExperience")
    DailyPatientLimit: int | None
    specialityID: int | None = Field(validation_alias="specialtyId")
    hospitalID: int | None = Field(validation_alias="hospitalId")


class DoctorAvailabilityCreate(BaseModel):
    """One recurring weekly availability slot for a doctor."""

    doctorId: int = Field(gt=0)
    day: Weekday
    startTime: time
    endTime: time

    @model_validator(mode="after")
    def end_time_must_follow_start_time(self):
        if self.endTime <= self.startTime:
            raise ValueError("endTime must be later than startTime")
        return self


class DoctorAvailabilityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    availability_id: int = Field(validation_alias="id")
    doctorID: int | None = Field(validation_alias="doctorId")
    day: str | None
    start_time: time | None = Field(validation_alias="startTime")
    end_time: time | None = Field(validation_alias="endTime")


class SpecialityCreate(BaseModel):
    specialityName: str = Field(min_length=1, max_length=120)

    @field_validator("specialityName")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Speciality name must not be blank")
        return value


class SpecialityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    specialityID: int = Field(
        validation_alias=AliasChoices("specialityID", "id")
    )
    specialityName: str = Field(
        validation_alias=AliasChoices("specialityName", "name")
    )


class DoctorTimingResponse(BaseModel):
    day: str
    startTime: time
    endTime: time


class DoctorCardResponse(BaseModel):
    """Doctor and related details used to render a doctor card."""

    doctorID: int
    Name: str | None
    YearsofExperience: int | None
    DailyPatientLimit: int | None
    specialityID: int | None
    specialityName: str | None
    hospitalID: int | None
    hospitalName: str | None
    City: str | None
    timings: list[DoctorTimingResponse] = Field(default_factory=list)


class DoctorFilterOptionsResponse(BaseModel):
    """Available values for the doctor directory filters."""

    specialities: list[SpecialityRead]
    cities: list[str]








from pydantic import BaseModel, Field

from schemas.DoctorSpecialities import SpecialityRead


class DoctorTimingResponse(BaseModel):
    day: str
    startTime: str
    endTime: str


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

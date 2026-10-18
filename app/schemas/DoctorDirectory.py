from pydantic import BaseModel

from schemas.DoctorSpecialities import SpecialityRead


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


class DoctorFilterOptionsResponse(BaseModel):
    """Available values for the doctor directory filters."""

    specialities: list[SpecialityRead]
    cities: list[str]

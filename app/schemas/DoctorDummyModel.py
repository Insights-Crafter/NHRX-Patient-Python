from pydantic import BaseModel, ConfigDict, Field, field_validator


class DoctorCreate(BaseModel):
    """Input required to create a doctor row."""

    Name: str = Field(min_length=1, max_length=120)
    YearsofExperience: int = Field(ge=0)
    DailyPatientLimit: int = Field(gt=0)
    specialityID: int = Field(gt=0)
    hospitalID: int = Field(gt=0)

    @field_validator("Name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Doctor name must not be blank")
        return value


class DoctorRead(DoctorCreate):
    """Doctor data returned from the API, including its generated ID."""

    model_config = ConfigDict(from_attributes=True)

    doctorID: int

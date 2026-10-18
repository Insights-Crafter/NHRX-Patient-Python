from pydantic import BaseModel, ConfigDict, Field, field_validator


class SpecialityCreate(BaseModel):
    specialityName: str = Field(min_length=1, max_length=120)

    @field_validator("specialityName")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Speciality name must not be blank")
        return value


class SpecialityRead(SpecialityCreate):
    model_config = ConfigDict(from_attributes=True)

    specialityID: int

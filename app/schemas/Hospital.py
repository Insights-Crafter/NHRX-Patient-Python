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


class HospitalRead(HospitalCreate):
    model_config = ConfigDict(from_attributes=True)

    hospitalID: int

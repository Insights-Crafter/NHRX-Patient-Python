from pydantic import BaseModel, Field, ConfigDict,  field_validator
from datetime import date, time, datetime

import datetime

class AppointmentCreate(BaseModel):
    DoctorID: int = Field(gt=0)
    AppointmentDate: date
    AppointmentTime: time
    Complaint: str = Field(min_length=1, max_length=1000)

    @field_validator("Complaint")
    @classmethod
    def validate_complaint(cls, value:str):
        value = value.strip()
        if not value:
            raise ValueError("Complaint cannot be empty")

        return value

class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    AppointmentID: int
    patientID: int
    DoctorID: int
    AppointmentDate: date
    AppointmentTime: time
    Complaint: str
    Booked_at: datetime


class AppointmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    AppointmentDate: date | None = None
    AppointmentTime: time | None = None
    Complaint: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )
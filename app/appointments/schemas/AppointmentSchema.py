from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AppointmentCreate(BaseModel):
    DoctorID: int = Field(gt=0)
    AppointmentDate: date
    AppointmentTime: time
    Complaint: str = Field(min_length=1, max_length=1000)

    @field_validator("Complaint")
    @classmethod
    def validate_complaint(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Complaint cannot be empty")
        return value


class AppointmentReschedule(BaseModel):
    AppointmentDate: date
    AppointmentTime: time


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    AppointmentID: int
    patientID: int
    DoctorID: int
    AppointmentDate: date
    AppointmentTime: time
    Complaint: str
    Booked_at: datetime | None


class AppointmentDetail(AppointmentResponse):
    doctorName: str | None = None
    specialityName: str | None = None
    hospitalName: str | None = None
    City: str | None = None


class DoctorPatientDetails(BaseModel):
    name: str
    dateOfBirth: str | None = None
    gender: str | None = None
    bloodGroup: str | None = None


class DoctorAppointmentResponse(BaseModel):
    appointmentDate: date
    appointmentTime: time
    complaint: str | None = None
    patient: DoctorPatientDetails


class AppointmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    AppointmentDate: date | None = None
    AppointmentTime: time | None = None
    Complaint: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def require_update(self):
        if self.AppointmentDate is None and self.AppointmentTime is None and self.Complaint is None:
            raise ValueError("Provide at least one appointment field to update")
        return self

from datetime import date

from pydantic import BaseModel, ConfigDict


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

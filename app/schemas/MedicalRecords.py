from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MedicalRecordsCreate(BaseModel):
    patientID: int | None = None
    doctorID: int | None = None
    hospitalID: int | None = None
    recordDATE: datetime | None = None
    recordType: str | None = None
    cheif_complaint: str | None = None
    follow_up_date: date | None = None


class MedicalRecordsRead(MedicalRecordsCreate):
    model_config = ConfigDict(from_attributes=True)

    recordID: int

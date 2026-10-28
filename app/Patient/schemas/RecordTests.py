from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicalRecordTestCreate(BaseModel):
    record_id: int
    test_id: int
    performed_at: datetime | None = None
    result: str | None = None
    status: str = "pending"


class MedicalRecordTestRead(MedicalRecordTestCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

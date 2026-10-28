from pydantic import BaseModel, ConfigDict


class RecordSymptomCreate(BaseModel):
    record_id: int
    symptom_id: int
    severity: str | None = None
    duration_days: int | None = None
    notes: str | None = None


class RecordSymptomRead(RecordSymptomCreate):
    model_config = ConfigDict(from_attributes=True)

    record_symptom_id: int

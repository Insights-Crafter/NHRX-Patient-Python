from pydantic import BaseModel, ConfigDict


class RecordMedicinesCreate(BaseModel):
    medicineID: int | None = None
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    duration_days: int | None = None


class RecordMedicinesRead(RecordMedicinesCreate):
    model_config = ConfigDict(from_attributes=True)

    recordID: int

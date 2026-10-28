from pydantic import BaseModel, ConfigDict


class SymptomCreate(BaseModel):
    name: str
    code: str | None = None


class SymptomRead(SymptomCreate):
    model_config = ConfigDict(from_attributes=True)

    symptom_id: int

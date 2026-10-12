from pydantic import BaseModel, ConfigDict


class MedicationsCreate(BaseModel):
    MedicineName: str | None = None
    Formula: str | None = None
    Strength: str | None = None


class MedicationsRead(MedicationsCreate):
    model_config = ConfigDict(from_attributes=True)

    MedID: int

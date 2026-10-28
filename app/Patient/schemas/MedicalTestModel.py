from pydantic import BaseModel, ConfigDict


class MedicalTestCreate(BaseModel):
    name: str
    description: str | None = None


class MedicalTestRead(MedicalTestCreate):
    model_config = ConfigDict(from_attributes=True)

    test_id: int

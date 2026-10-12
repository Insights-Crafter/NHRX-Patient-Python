from pydantic import BaseModel, ConfigDict


class RecordDiagnosisCreate(BaseModel):
    recordID: int | None = None
    Diagnosis: str | None = None
    Diagnosisnotes: str | None = None


class RecordDiagnosisRead(RecordDiagnosisCreate):
    model_config = ConfigDict(from_attributes=True)

    noteID: int

from pydantic import BaseModel, ConfigDict


class ClinicalNotesCreate(BaseModel):
    recordID: int | None = None
    DiagnosisID: int | None = None
    Notes: str | None = None


class ClinicalNotesRead(ClinicalNotesCreate):
    model_config = ConfigDict(from_attributes=True)

    noteID: int

from database.database import Base
from sqlalchemy import Column , Integer ,  ForeignKey, TIMESTAMP, String


class ClinicalNotes(Base):
    __tablename__ = "ClinicalNotes"

    noteID = Column(Integer, primary_key=True)
    recordID = Column(Integer, ForeignKey("MedicalRecords.recordID"))
    DiagnosisID = Column(Integer, ForeignKey("RecordDiagnosis.diagnosisID"))
    Notes = Column(String)

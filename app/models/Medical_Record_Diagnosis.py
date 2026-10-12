from database.database import Base
from sqlalchemy import Column , Integer ,  ForeignKey, TIMESTAMP, String


class ClinicalNotes(Base):
    __tablename__ = "RecordDiagnosis"

    diagnosisID = Column(Integer, primary_key=True)
    recordID = Column(Integer, ForeignKey("MedicalRecords.recordID"))
    Diagnosis = Column(String)
    Diagnosisnotes = Column(String)

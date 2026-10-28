from sqlalchemy import Column, Integer, String, ForeignKey, TEXT

from database.database import Base

class RecordSymptom(Base):
    __tablename__ = "record_symptoms"
    
 
    record_symptom_id = Column(Integer, primary_key=True)
    record_id = Column(
        Integer,
        ForeignKey("MedicalRecords.recordID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    symptom_id = Column(
        Integer,
        ForeignKey("symptoms.symptom_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    severity = Column(String(20))
    duration_days = Column(Integer)
    notes = Column(TEXT)
 

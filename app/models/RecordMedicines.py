from sqlalchemy import Integer, String, Column, ForeignKey
from database.database import Base


class RecordMedicines(Base):
    __tablename__ = "RecordMedicines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("MedicalRecords.recordID"), nullable=False, index=True)
    medicineID = Column(Integer, ForeignKey("Medications.MedID"))
    dosage = Column(String)
    frequency = Column(String)
    duration_days = Column(Integer)
    

from database.database import Base
from sqlalchemy import Column , Integer ,  ForeignKey, TIMESTAMP, String, DATE

class MedicalRecords(Base):
    __tablename__ = "MedicalRecords"
    recordID = Column(Integer, primary_key=True)
    patientID = Column(Integer, ForeignKey("Patients.patientID"))
    doctorID = Column(Integer)
    hospitalID = Column(Integer)
    recordDATE = Column(TIMESTAMP)
    recordType = Column(String)
    cheif_complaint = Column(String)
    follow_up_date = Column(DATE)


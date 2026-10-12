from database.database import Base
from sqlalchemy import Column , Integer ,  ForeignKey, TIMESTAMP, String, TEXT


class AuthCredentials(Base):
    __tablename__ = "Authentication"

    authenticationID = Column(Integer,primary_key=True)
    patientID = Column(Integer,ForeignKey("Patients.patientID"))
    nationalID = Column(TEXT,ForeignKey("Patients.nationalID"))
    password = Column(TEXT)
    

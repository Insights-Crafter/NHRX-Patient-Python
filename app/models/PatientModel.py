from sqlalchemy import Integer, Column, Text, TIMESTAMP
from database.database import Base


class Patient(Base):
    __tablename__ = "Patients"
    patientID = Column(Integer,primary_key=True)
    # PII fields use Text so they can hold variable-length encrypted values.
    nationalID = Column(Text,unique=True)
    firstName = Column(Text)
    lastName = Column(Text)
    date_of_birth = Column(Text)
    blood_group = Column(Text)
    gender = Column(Text)
    phone = Column(Text)
    email = Column(Text)
    createdAt = Column(TIMESTAMP)





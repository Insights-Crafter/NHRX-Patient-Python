from sqlalchemy import Integer, Column, ForeignKey, Text
from database.database import Base

class PatientAddress(Base):
    __tablename__ = "PatientAddress"
    AddressID = Column(Integer, primary_key=True)
    patientID = Column(Integer, ForeignKey("Patients.patientID", ondelete="CASCADE", onupdate="CASCADE"))
    # Address fields may contain encrypted values, whose length can exceed
    # the plaintext value's length.
    Area = Column(Text)
    HouseNumber = Column(Text)
    Province = Column(Text)
    City = Column(Text)
    Street = Column(Text)
    Block = Column(Text)

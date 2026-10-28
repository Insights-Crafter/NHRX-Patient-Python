from sqlalchemy import Column, ForeignKey, Integer, TEXT

from database.database import Base


class Doctor(Base):
    __tablename__ = "Doctor"

    id = Column(Integer, primary_key=True)
    name = Column(TEXT)
    yearsofExperience = Column(Integer)
    dailyPatientLimit = Column(Integer)
    specialtyId = Column(Integer, ForeignKey("Specialities.id"))
    hospitalId = Column(Integer, ForeignKey("Hospitals.hospitalID"))
    

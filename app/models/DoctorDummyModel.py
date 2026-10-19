from sqlalchemy import Column, String, TIMESTAMP, DATE, Integer, TEXT, ForeignKey

from database.database import Base


class DoctorDummy(Base):
    __tablename__ = "Doctor_Dummy"

    doctorID = Column(Integer, primary_key=True)
    Name = Column(String)
    YearsofExperience = Column(Integer)
    DailyPatientLimit = Column(Integer)
    specialityID = Column(Integer, ForeignKey("Specialities_Dummy.specialityID"))
    hospitalID = Column(Integer,ForeignKey("Hospitals.hospitalID"))


 

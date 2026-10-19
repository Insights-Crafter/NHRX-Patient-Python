from sqlalchemy import TIME, Column, Integer, String, ForeignKey

from database.database import Base


class DoctorAvailability(Base):
    __tablename__ = "DoctorTimings_Dummy"
    availability_id = Column(Integer,primary_key=True)
    doctorID = Column(Integer,ForeignKey("Doctor_Dummy.doctorID"))
    day = Column(String)
    start_time = Column(TIME)
    end_time = Column(TIME)
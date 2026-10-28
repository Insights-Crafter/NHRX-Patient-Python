from sqlalchemy import TIME, Column, Integer, String, ForeignKey, TEXT

from database.database import Base


class DoctorAvailability(Base):
    __tablename__ = "DoctorTimings"
    id = Column(Integer,primary_key=True)
    doctorId = Column(Integer, ForeignKey("Doctor.id", ondelete="SET NULL", onupdate="CASCADE"))
    day = Column(TEXT)
    startTime = Column(TIME)
    endTime = Column(TIME)

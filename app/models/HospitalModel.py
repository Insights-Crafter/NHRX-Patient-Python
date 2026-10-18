from sqlalchemy import Column, String, TIMESTAMP, DATE, Integer, TEXT, ForeignKey

from database.database import Base



class Hospital(Base):
    __tablename__ = "Hospitals"

    hospitalID = Column(Integer, primary_key=True)
    hospitalName = Column(String)
    City = Column(String)
    
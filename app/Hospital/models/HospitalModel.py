from sqlalchemy import Column, Integer, String

from database.database import Base



class Hospital(Base):
    __tablename__ = "Hospitals"

    hospitalID = Column(Integer, primary_key=True)
    hospitalName = Column(String)
    City = Column(String)
    

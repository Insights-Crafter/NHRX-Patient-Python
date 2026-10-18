from sqlalchemy import Column, String, TIMESTAMP, DATE, Integer, TEXT, ForeignKey

from database.database import Base



class Specialities(Base):
    __tablename__ = "Specialities"

    specialityID = Column(Integer, primary_key=True)
    specialityName = Column(String)


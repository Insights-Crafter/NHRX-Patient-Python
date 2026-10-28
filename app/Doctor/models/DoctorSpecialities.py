from sqlalchemy import Column, String, TIMESTAMP, DATE, Integer, TEXT, ForeignKey

from database.database import Base



class Specialities(Base):
    __tablename__ = "Specialities"

    id = Column(Integer, primary_key=True)
    name = Column(TEXT)


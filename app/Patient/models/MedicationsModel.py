from database.database import Base
from sqlalchemy import Column , Integer, String


class Medications(Base):
    __tablename__ = "Medications"
    MedID = Column(Integer, primary_key=True)
    MedicineName = Column(String)
    Formula = Column(String)
    Strength = Column(String)

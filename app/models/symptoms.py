from sqlalchemy import Column, Integer, String

from database.database import Base

class Symptom(Base):
    __tablename__ = "symptoms"
 
    symptom_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(50))
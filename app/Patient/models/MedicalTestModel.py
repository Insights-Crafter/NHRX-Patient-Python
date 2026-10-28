# MEDICAL_TEST
from sqlalchemy import Column, Integer, String, Text
from database.database import Base


class MedicalTest(Base):
    __tablename__ = "medical_tests"

    test_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(Text)
from sqlalchemy import Column, ForeignKey, Integer, Text

from database.database import Base
from utilityfunctions.passwords import hash_password


class DoctorAuthentication(Base):
    __tablename__ = "DoctorAuthentication"

    doctorId = Column(
        Integer,
        ForeignKey("Doctor.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    passwordHash = Column(Text, nullable=False)

    def __init__(self, doctorId: int, password: str):
       
        self.doctorId = doctorId
        self.passwordHash = hash_password(password)

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from database.database import Base


class PatientDocument(Base):
    __tablename__ = "PatientDocuments"

    documentID = Column(Integer, primary_key=True, autoincrement=True)
    patientID = Column(Integer, ForeignKey("Patients.patientID", ondelete="CASCADE"), nullable=False, index=True)
    doctorID = Column(Integer, ForeignKey("Doctor.id", ondelete="SET NULL"), nullable=True, index=True)
    appointmentID = Column(Integer, ForeignKey("Appointments.AppointmentID", ondelete="SET NULL"), nullable=True, index=True)
    documentType = Column(String(20), nullable=False, index=True)
    fileName = Column(String(255), nullable=False)
    description = Column(Text)
    objectKey = Column(String(512), nullable=False, unique=True)
    contentType = Column(String(32), nullable=False)
    fileSize = Column(Integer, nullable=False)
    uploadedAt = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

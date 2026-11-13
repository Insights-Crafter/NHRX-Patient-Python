from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from database.database import Base


class PatientImage(Base):
    __tablename__ = "PatientImages"

    imageID = Column(Integer, primary_key=True, autoincrement=True)
    patientID = Column(
        Integer,
        ForeignKey("Patients.patientID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    # Persist only the private R2 object key; never store an expiring URL here.
    objectKey = Column(String(512), nullable=False, unique=True)
    contentType = Column(String(32), nullable=False)
    fileSize = Column(Integer, nullable=False)
    uploadedAt = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

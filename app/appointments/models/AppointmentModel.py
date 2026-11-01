from sqlalchemy import Column, String, TIMESTAMP, DATE, Integer, TEXT, ForeignKey, TIME, CheckConstraint

from database.database import Base


class Appointments(Base):
    __tablename__ = "Appointments"

    __table_args__ = (
        CheckConstraint(
            '"Status" IN (\'Pending\', \'Completed\', \'Rejected\')',
            name="ck_appointments_status",
        ),
    )

    

    AppointmentID = Column(Integer, primary_key=True)
    patientID = Column(Integer,ForeignKey("Patients.patientID"))
    DoctorID = Column(Integer, ForeignKey("Doctor.id"))
    AppointmentDate = Column(DATE)
    AppointmentTime = Column(TIME)
    Complaint = Column(String)
    Booked_at = Column(TIMESTAMP)
    Status = Column(String)


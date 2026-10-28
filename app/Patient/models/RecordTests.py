
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from database.database import Base


class MedicalRecordTest(Base):
    __tablename__ = "medical_record_tests"
    __table_args__ = (
        UniqueConstraint("record_id", "test_id", "performed_at", name="uq_record_test_time"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(
        Integer,
        ForeignKey("MedicalRecords.recordID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id = Column(
        Integer,
        ForeignKey("medical_tests.test_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    performed_at = Column(DateTime(timezone=True))
    result = Column(Text)
    status = Column(String(20), nullable=False, default="pending")  # pending / completed / cancelled

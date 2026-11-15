"""Create metadata for private doctor-uploaded patient documents.

Revision ID: d4f8a2c6e9b1
Revises: c8d2e4f6a1b3
Create Date: 2026-11-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4f8a2c6e9b1"
down_revision: Union[str, Sequence[str], None] = "c8d2e4f6a1b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "PatientDocuments",
        sa.Column("documentID", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patientID", sa.Integer(), nullable=False),
        sa.Column("doctorID", sa.Integer(), nullable=True),
        sa.Column("appointmentID", sa.Integer(), nullable=True),
        sa.Column("documentType", sa.String(length=20), nullable=False),
        sa.Column("fileName", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("objectKey", sa.String(length=512), nullable=False),
        sa.Column("contentType", sa.String(length=32), nullable=False),
        sa.Column("fileSize", sa.Integer(), nullable=False),
        sa.Column("uploadedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["patientID"], ["public.Patients.patientID"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["doctorID"], ["public.Doctor.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["appointmentID"], ["public.Appointments.AppointmentID"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("documentID"),
        sa.UniqueConstraint("objectKey", name="uq_patient_documents_object_key"),
        sa.CheckConstraint('"documentType" IN (\'report\', \'prescription\')', name="ck_patient_documents_type"),
        schema="public",
    )
    op.create_index("ix_public_PatientDocuments_patientID", "PatientDocuments", ["patientID"], schema="public")
    op.create_index("ix_public_PatientDocuments_doctorID", "PatientDocuments", ["doctorID"], schema="public")
    op.create_index("ix_public_PatientDocuments_appointmentID", "PatientDocuments", ["appointmentID"], schema="public")
    op.create_index("ix_public_PatientDocuments_documentType", "PatientDocuments", ["documentType"], schema="public")


def downgrade() -> None:
    op.drop_index("ix_public_PatientDocuments_documentType", table_name="PatientDocuments", schema="public")
    op.drop_index("ix_public_PatientDocuments_appointmentID", table_name="PatientDocuments", schema="public")
    op.drop_index("ix_public_PatientDocuments_doctorID", table_name="PatientDocuments", schema="public")
    op.drop_index("ix_public_PatientDocuments_patientID", table_name="PatientDocuments", schema="public")
    op.drop_table("PatientDocuments", schema="public")

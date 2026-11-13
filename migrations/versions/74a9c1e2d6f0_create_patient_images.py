"""Create private patient image metadata table.

Revision ID: 74a9c1e2d6f0
Revises: e2cbefd82554
Create Date: 2026-11-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "74a9c1e2d6f0"
down_revision: Union[str, Sequence[str], None] = "e2cbefd82554"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "PatientImages",
        sa.Column("imageID", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patientID", sa.Integer(), nullable=False),
        sa.Column("objectKey", sa.String(length=512), nullable=False),
        sa.Column("contentType", sa.String(length=32), nullable=False),
        sa.Column("fileSize", sa.Integer(), nullable=False),
        sa.Column("uploadedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["patientID"], ["public.Patients.patientID"],
            name="fk_patient_images_patient_id", ondelete="CASCADE", onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("imageID", name="pk_patient_images"),
        sa.UniqueConstraint("objectKey", name="uq_patient_images_object_key"),
        schema="public",
    )
    op.create_index("ix_public_PatientImages_patientID", "PatientImages", ["patientID"], schema="public")


def downgrade() -> None:
    op.drop_index("ix_public_PatientImages_patientID", table_name="PatientImages", schema="public")
    op.drop_table("PatientImages", schema="public")

"""Give existing doctors a full weekly schedule where days are missing.

Revision ID: 91b7c8a4d2e1
Revises: 74a9c1e2d6f0
Create Date: 2026-11-14
"""

from typing import Sequence, Union

from alembic import op


revision: str = "91b7c8a4d2e1"
down_revision: Union[str, Sequence[str], None] = "74a9c1e2d6f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing days keep their configured hours; only missing weekdays receive
    # the default 09:00–17:00 clinic window.
    op.execute("""
        INSERT INTO "DoctorTimings" ("doctorId", day, "startTime", "endTime")
        SELECT d.id, days.day, TIME '09:00', TIME '17:00'
        FROM "Doctor" AS d
        CROSS JOIN (VALUES
            ('Monday'), ('Tuesday'), ('Wednesday'), ('Thursday'),
            ('Friday'), ('Saturday'), ('Sunday')
        ) AS days(day)
        WHERE NOT EXISTS (
            SELECT 1 FROM "DoctorTimings" AS t
            WHERE t."doctorId" = d.id AND lower(t.day) = lower(days.day)
        )
    """)


def downgrade() -> None:
    # Added hours are indistinguishable from manually configured 09:00–17:00
    # rows, so downgrade leaves schedule data intact.
    pass

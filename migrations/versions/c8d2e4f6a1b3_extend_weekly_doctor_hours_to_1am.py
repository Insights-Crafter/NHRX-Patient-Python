"""Extend every doctor's weekly schedule through 01:00, including Sunday.

Revision ID: c8d2e4f6a1b3
Revises: b43d91e60f27
Create Date: 2026-11-15
"""

from typing import Sequence, Union

from alembic import op


revision: str = "c8d2e4f6a1b3"
down_revision: Union[str, Sequence[str], None] = "b43d91e60f27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Keep configured start times. Store 01:00 as a wraparound end time;
    # booking logic interprets it as the overnight boundary.
    op.execute('''
        UPDATE "DoctorTimings"
        SET "endTime" = TIME '01:00'
        WHERE "endTime" IS DISTINCT FROM TIME '01:00'
    ''')
    op.execute('''
        INSERT INTO "DoctorTimings" ("doctorId", day, "startTime", "endTime")
        SELECT d.id, 'Sunday', TIME '09:00', TIME '01:00'
        FROM "Doctor" AS d
        WHERE NOT EXISTS (
            SELECT 1 FROM "DoctorTimings" AS t
            WHERE t."doctorId" = d.id AND lower(t.day) = 'sunday'
        )
    ''')


def downgrade() -> None:
    # Original closing times were not tracked, so schedule data is retained.
    pass

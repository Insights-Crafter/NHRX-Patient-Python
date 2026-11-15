"""Extend Saturday doctor availability through 21:00.

Revision ID: b43d91e60f27
Revises: 91b7c8a4d2e1
Create Date: 2026-11-14
"""

from typing import Sequence, Union

from alembic import op


revision: str = "b43d91e60f27"
down_revision: Union[str, Sequence[str], None] = "91b7c8a4d2e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('''
        UPDATE "DoctorTimings"
        SET "endTime" = TIME '21:00'
        WHERE lower(day) = 'saturday'
          AND "endTime" < TIME '21:00'
    ''')


def downgrade() -> None:
    # Original Saturday closing times vary by doctor and are not stored
    # separately, so the extended hours are retained on downgrade.
    pass

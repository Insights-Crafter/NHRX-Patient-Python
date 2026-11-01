"""Added status column in  appointments table

Revision ID: e2cbefd82554
Revises: 
Create Date: 2026-11-01 22:11:47.642607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2cbefd82554'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "Appointments",
        sa.Column("Status", sa.String(), nullable=True),
    )
    op.create_check_constraint(
        "ck_appointments_status",
        "Appointments",
        '"Status" IN (\'Pending\', \'Completed\', \'Rejected\')',
    )

def downgrade() -> None:
    op.drop_constraint(
        "ck_appointments_status",
        "Appointments",
        type_="check",
    )
    op.drop_column("Appointments", "Status")

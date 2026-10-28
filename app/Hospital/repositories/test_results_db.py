"""Print examples of SQLAlchemy Result, ScalarResult, and scalar() values."""

from pathlib import Path
import sys

APP_DIR = str(Path(__file__).resolve().parents[2])
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.database import SessionLocal
from Hospital.models.HospitalModel import Hospital


def get_all_hospitals(db: Session) -> list[Hospital]:
    """Return every Hospital ORM object using Session.scalars()."""
    statement = select(Hospital).order_by(Hospital.hospitalID)
    return list(db.scalars(statement).all())


def get_all_hospital_names(db: Session) -> list[str | None]:
    """Return just the hospitalName column for every hospital."""
    statement = select(Hospital.hospitalName).order_by(Hospital.hospitalID)
    db


def print_sqlalchemy_results() -> None:
    with SessionLocal() as db:
        # execute(...).all() returns Row objects. Selecting the model means
        # each Row contains one Hospital ORM object.
        hospital_statement = select(Hospital).order_by(Hospital.hospitalID)
        result = db.execute(hospital_statement)
        rows = result.all()
        print("db.execute(select(Hospital)).all():")
        print(rows)

        # scalars(...).all() unwraps the Hospital object from each Row.
        hospitals = get_all_hospitals(db)
        print("\ndb.scalars(select(Hospital)).all():")
        print(hospitals)
        print("Hospital field values:")
        print([
            {
                "hospitalID": hospital.hospitalID,
                "hospitalName": hospital.hospitalName,
                "City": hospital.City,
            }
            for hospital in hospitals
        ])

        # Selecting one column makes execute().all() return one-column Rows.
        name_statement = select(Hospital.hospitalName).order_by(
            Hospital.hospitalID
        )
        name_rows = db.execute(name_statement).all()
        print("\ndb.execute(select(Hospital.hospitalName)).all():")
        print(name_rows)

        # scalars(...).all() unwraps the first column from every Row.
        print("\ndb.scalars(select(Hospital.hospitalName)).all():")
        print(get_all_hospital_names(db))

        # scalar() returns only the first column of the first matching row.
        first_name_statement = name_statement.limit(1)
        print("\ndb.scalar(select(Hospital.hospitalName).limit(1)):")
        print(db.scalar(first_name_statement))


if __name__ == "__main__":
    print_sqlalchemy_results()

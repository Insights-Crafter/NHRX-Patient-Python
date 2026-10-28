from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import Session

from Hospital.models.HospitalModel import Hospital


def get_hospital_name(
    hospitalID: int,
    db: Session,
) -> str | None:
    statement = select(Hospital.hospitalName).where(
        Hospital.hospitalID == hospitalID
    )
    return db.scalar(statement)


def hospital_name_exists(
    hospitalName: str,
    db: Session,
) -> bool:
    """Return whether any hospital already has this name."""
    statement = select(Hospital.hospitalID).where(
        func.lower(func.trim(Hospital.hospitalName)) == hospitalName.strip().lower(),
    )
    existing_hospital_id = db.scalar(statement)
    if existing_hospital_id is not None:
        return True
    return False




def updateHospitalname(
    newName: str,
    db: Session,
    requestID: int,
    ) -> bool:
    statement = (
        update(Hospital)
        .where(Hospital.hospitalID == requestID)
        .values({Hospital.hospitalName: newName})
    )
    result = db.execute(statement)
    return result.rowcount == 1


def createHospital(name: str, city: str, db: Session) -> Hospital:
    statement = (
        insert(Hospital)
        .values(hospitalName=name, City=city)
        .returning(Hospital)
    )
    return db.scalars(statement).one()





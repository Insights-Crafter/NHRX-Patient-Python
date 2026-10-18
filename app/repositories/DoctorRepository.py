
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.DoctorDummyModel import DoctorDummy
from models.DoctorSpecialities import Specialities
from models.HospitalModel import Hospital


class DoctorRepository:
    def __init__(self, db):
        self.db = db

    def search_doctors(
    self,
    search: str | None = None,
    speciality_id: int | None = None,
    city: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
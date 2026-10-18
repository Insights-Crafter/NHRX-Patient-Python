from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.AuthCredModel import AuthCredentials
from models.PatientAddress import PatientAddress
from models.PatientModel import Patient

from models.DoctorDummyModel import DoctorDummy


class AppointmentRepository:
    def __init__(self, db: Session):
            self.db = db

    def find_doctor_by_id(self,doctorID):
         return self.db.query(DoctorDummy).filter(DoctorDummy.doctorID==doctorID).first()

    
        
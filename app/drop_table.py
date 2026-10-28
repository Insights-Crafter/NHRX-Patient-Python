from database.database import engine

from Doctor.models.DoctorModel import Doctor

Doctor.__table__.drop(bind=engine)

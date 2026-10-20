from database.database import engine

from models.DoctorModel import Doctor

Doctor.__table__.drop(bind=engine)

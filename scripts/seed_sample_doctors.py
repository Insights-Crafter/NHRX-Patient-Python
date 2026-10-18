"""Idempotently seed sample doctor directory data into the configured PostgreSQL DB.

Run from the project root with: venv/Scripts/python.exe scripts/seed_sample_doctors.py
"""

from datetime import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from database.database import SessionLocal  # noqa: E402
from models.DoctorAvailbilityModel import DoctorAvailability  # noqa: E402
from models.DoctorDummyModel import DoctorDummy  # noqa: E402
from models.DoctorSpecialities import Specialities  # noqa: E402
from models.HospitalModel import Hospital  # noqa: E402


SAMPLE_DOCTORS = [
    ("Ayesha Rahman", "Cardiology", "Crescent City Hospital", "Karachi", 12, 18),
    ("Hamza Siddiqui", "Cardiology", "River View Medical Centre", "Lahore", 9, 20),
    ("Sara Khan", "Dermatology", "Crescent City Hospital", "Karachi", 8, 16),
    ("Usman Malik", "Dermatology", "Capital Care Hospital", "Islamabad", 14, 15),
    ("Mariam Ahmed", "Neurology", "River View Medical Centre", "Lahore", 11, 12),
    ("Bilal Hussain", "Neurology", "Capital Care Hospital", "Islamabad", 7, 14),
    ("Noor Fatima", "Pediatrics", "Crescent City Hospital", "Karachi", 10, 22),
    ("Zain Abbas", "Pediatrics", "River View Medical Centre", "Lahore", 6, 18),
    ("Hira Iqbal", "Orthopedics", "Capital Care Hospital", "Islamabad", 13, 16),
    ("Omar Farooq", "Orthopedics", "Crescent City Hospital", "Karachi", 16, 14),
    ("Kiran Shah", "Gynecology", "River View Medical Centre", "Lahore", 9, 20),
    ("Daniyal Raza", "Gynecology", "Capital Care Hospital", "Islamabad", 5, 12),
]


def seed_sample_doctors() -> tuple[int, int]:
    session = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        specialities = {
            row.specialityName.casefold(): row
            for row in session.query(Specialities).all()
            if row.specialityName
        }
        hospitals = {
            (row.hospitalName.casefold(), (row.City or "").casefold()): row
            for row in session.query(Hospital).all()
            if row.hospitalName
        }

        for name, speciality_name, hospital_name, city, experience, daily_limit in SAMPLE_DOCTORS:
            speciality = specialities.get(speciality_name.casefold())
            if speciality is None:
                speciality = Specialities(specialityName=speciality_name)
                session.add(speciality)
                session.flush()
                specialities[speciality_name.casefold()] = speciality

            hospital_key = (hospital_name.casefold(), city.casefold())
            hospital = hospitals.get(hospital_key)
            if hospital is None:
                hospital = Hospital(hospitalName=hospital_name, City=city)
                session.add(hospital)
                session.flush()
                hospitals[hospital_key] = hospital

            existing = (
                session.query(DoctorDummy)
                .filter(
                    DoctorDummy.Name == name,
                    DoctorDummy.specialityID == speciality.specialityID,
                    DoctorDummy.hospitalID == hospital.hospitalID,
                )
                .first()
            )
            if existing:
                skipped += 1
                continue

            doctor = DoctorDummy(
                Name=name,
                YearsofExperience=experience,
                DailyPatientLimit=daily_limit,
                specialityID=speciality.specialityID,
                hospitalID=hospital.hospitalID,
            )
            session.add(doctor)
            session.flush()
            session.add_all(
                [
                    DoctorAvailability(
                        doctorID=doctor.doctorID,
                        day="Monday",
                        start_time=time(9, 0),
                        end_time=time(13, 0),
                    ),
                    DoctorAvailability(
                        doctorID=doctor.doctorID,
                        day="Wednesday",
                        start_time=time(14, 0),
                        end_time=time(18, 0),
                    ),
                ]
            )
            inserted += 1

        session.commit()
        return inserted, skipped
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    inserted_count, skipped_count = seed_sample_doctors()
    print(f"Inserted sample doctors: {inserted_count}")
    print(f"Skipped existing sample doctors: {skipped_count}")
    print("Each new doctor has Monday and Wednesday availability.")

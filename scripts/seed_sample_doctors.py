"""Idempotently seed sample doctor directory data into the configured PostgreSQL DB.

Run from the project root with: venv/Scripts/python.exe scripts/seed_sample_doctors.py
"""

from datetime import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from database.database import SessionLocal  # noqa: E402
from Doctor.models.DoctorAvailbilityModel import DoctorAvailability  # noqa: E402
from Doctor.models.DoctorModel import Doctor  # noqa: E402
from Doctor.models.DoctorSpecialities import Specialities  # noqa: E402
from Hospital.models.HospitalModel import Hospital  # noqa: E402


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
            row.name.casefold(): row
            for row in session.query(Specialities).all()
            if row.name
        }
        hospitals = {
            (row.hospitalName.casefold(), (row.City or "").casefold()): row
            for row in session.query(Hospital).all()
            if row.hospitalName
        }

        for name, speciality_name, hospital_name, city, experience, daily_limit in SAMPLE_DOCTORS:
            speciality = specialities.get(speciality_name.casefold())
            if speciality is None:
                speciality = Specialities(name=speciality_name)
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
                session.query(Doctor)
                .filter(
                    Doctor.name == name,
                    Doctor.specialtyId == speciality.id,
                    Doctor.hospitalId == hospital.hospitalID,
                )
                .first()
            )
            if existing:
                skipped += 1
                continue

            doctor = Doctor(
                name=name,
                yearsofExperience=experience,
                dailyPatientLimit=daily_limit,
                specialtyId=speciality.id,
                hospitalId=hospital.hospitalID,
            )
            session.add(doctor)
            session.flush()
            session.add_all(
                [
                    DoctorAvailability(
                        doctorId=doctor.id,
                        day="Monday",
                        startTime="09:00",
                        endTime="13:00",
                    ),
                    DoctorAvailability(
                        doctorId=doctor.id,
                        day="Wednesday",
                        startTime="14:00",
                        endTime="18:00",
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

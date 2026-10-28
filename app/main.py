"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import os
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Support both ``uvicorn main:app --app-dir app`` and ``uvicorn app.main:app``.
APP_DIR = str(Path(__file__).resolve().parent)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from database.database import Base, engine
from Patient import models as patient_models
from Doctor import models as doctor_models
from Hospital import models as hospital_models
from appointments import models as appointment_models
from Patient.routes.PatientRegRoutes import router as patient_registration_router
from Patient.routes.PatientProfileRoutes import router as patient_profile_router
from Patient.routes.PatientUpdateRoutes import router as patient_update_router
from Patient.routes.Authentication import authRouter
from Doctor.routes.DoctorRoutes import router as doctor_router
from Hospital.routes.HospitalRoute import routerHospital as hospital_router
from appointments.routes.AppointmentRoutes import router as appointment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create doctor tables after deployment, or all tables when requested."""
    if os.getenv("CREATE_DB_TABLES", "false").strip().lower() in {"1", "true", "yes"}:
        Base.metadata.create_all(bind=engine)
    else:
        # These tables were dropped to be rebuilt. Keep regular startup scoped
        # to the doctor directory and its appointment table; patient schemas
        # remain managed separately.
        doctor_table_names = {
            "Specialities",
            "Hospitals",
            "Doctor",
            "DoctorTimings",
            "Appointments",
        }
        doctor_tables = [
            table
            for table in Base.metadata.sorted_tables
            if table.name in doctor_table_names
        ]
        Base.metadata.create_all(bind=engine, tables=doctor_tables)
    yield


app = FastAPI(
    title="NHRX API",
    lifespan=lifespan,
)

# Allow local browser frontends (for example, VS Code Live Server) to call
# FastAPI directly at http://localhost:8000 during development.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_registration_router)
app.include_router(patient_profile_router)
app.include_router(patient_update_router)
app.include_router(authRouter)
app.include_router(doctor_router)
app.include_router(hospital_router)
app.include_router(appointment_router)


@app.get("/", tags=["health"])
def read_root():
    return {"status": "ok", "message": "NHRX API is running"}

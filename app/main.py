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
import models 
from routes.PatientRegRoutes import router as patient_registration_router
from routes.PatientProfileRoutes import router as patient_profile_router
from routes.PatientUpdateRoutes import router as patient_update_router
from routes.Authentication import authRouter
from routes.DoctorRoutes import router as doctor_router
from routes.AppointmentRoutes import router as appointment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Optionally create missing tables for local development."""
    if os.getenv("CREATE_DB_TABLES", "false").strip().lower() in {"1", "true", "yes"}:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="NHRX Patient API",
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
app.include_router(appointment_router)


@app.get("/", tags=["health"])
def read_root():
    return {"status": "ok", "message": "NHRX Patient API is running"}

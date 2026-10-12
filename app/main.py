"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI

# Support both ``uvicorn main:app --app-dir app`` and ``uvicorn app.main:app``.
APP_DIR = str(Path(__file__).resolve().parent)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from database.database import Base, engine
import models  # noqa: F401 - registers every model with Base.metadata.
from routes.PatientRegRoutes import router as patient_registration_router
from routes.Authentication import authRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables before serving requests."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="NHRX Patient API",
    lifespan=lifespan,
)

app.include_router(patient_registration_router)
app.include_router(authRouter)


@app.get("/", tags=["health"])
def read_root():
    return {"status": "ok", "message": "NHRX Patient API is running"}

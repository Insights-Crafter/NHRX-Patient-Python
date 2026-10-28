from datetime import date, time

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.database import get_db
from appointments.schemas.AppointmentSchema import (
    AppointmentCreate,
    AppointmentDetail,
    AppointmentReschedule,
    AppointmentResponse,
)
from appointments.services.appointment_service import AppointmentService
from utilityfunctions.reusable_functions import extract_patient_id


router = APIRouter(tags=["appointments"])
bearer_scheme = HTTPBearer(auto_error=False)


def authenticated_patient_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    return extract_patient_id(credentials)


@router.get("/doctors/{doctor_id}/availability", response_model=list[time])
def get_doctor_availability(
    doctor_id: int,
    appointment_date: date = Query(alias="date"),
    db: Session = Depends(get_db),
) -> list[time]:
    return AppointmentService(db).get_available_slots(doctor_id, appointment_date)


@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    request: AppointmentCreate,
    patient_id: int = Depends(authenticated_patient_id),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    return AppointmentService(db).book_appointment(patient_id, request)


@router.get("/appointments", response_model=list[AppointmentDetail])
def list_appointments(
    patient_id: int = Depends(authenticated_patient_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    return AppointmentService(db).list_patient_appointments(patient_id)


@router.patch("/appointments/{appointment_id}", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: int,
    request: AppointmentReschedule,
    patient_id: int = Depends(authenticated_patient_id),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    return AppointmentService(db).reschedule_appointment(patient_id, appointment_id, request)


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: int,
    patient_id: int = Depends(authenticated_patient_id),
    db: Session = Depends(get_db),
) -> Response:
    AppointmentService(db).cancel_appointment(patient_id, appointment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

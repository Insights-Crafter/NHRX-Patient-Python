import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.database import get_db
from JWT.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from Doctor.schemas.DoctorSchemas import (
    DoctorCardResponse,
    DoctorFilterOptionsResponse,
    DoctorCreate,
    DoctorAvailabilityCreate,
    DoctorAvailabilityRead,
    DoctorPasswordCreate,
    DoctorPasswordCreated,
    DoctorLoginRequest,
    DoctorTokenResponse,
)
from Doctor.services.doctor_authentication import DoctorAuthenticationService
from Doctor.services.doctor_directory import DoctorDirectoryService
from appointments.schemas.AppointmentSchema import DoctorAppointmentResponse
from appointments.services.appointment_service import AppointmentService
from utilityfunctions.reusable_functions import extract_doctor_id


router = APIRouter(prefix="/doctors", tags=["doctors"])
bearer_scheme = HTTPBearer(auto_error=False)


def authenticated_doctor_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    return extract_doctor_id(credentials)


def require_doctor_password_setup_key(
    setup_key: str | None = Header(default=None, alias="X-Doctor-Setup-Key"),
) -> None:
    configured_key = os.getenv("DOCTOR_PASSWORD_SETUP_KEY")
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Doctor password setup is not enabled",
        )
    if setup_key is None or not hmac.compare_digest(
        setup_key.encode("utf-8"), configured_key.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid doctor password setup key",
        )


@router.get("", response_model=list[DoctorCardResponse])
def list_doctors_route(
    search: str | None = Query(default=None, max_length=120),
    speciality_id: int | None = Query(default=None, gt=0),
    city: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[DoctorCardResponse]:
    return DoctorDirectoryService(db).list_doctors(
        search=search,
        speciality_id=speciality_id,
        city=city,
        limit=limit,
        offset=offset,
    )


@router.get("/filters", response_model=DoctorFilterOptionsResponse)
def doctor_filter_options_route(
    db: Session = Depends(get_db),
) -> DoctorFilterOptionsResponse:
    return DoctorDirectoryService(db).get_filter_options()


@router.post("/auth/login", response_model=DoctorTokenResponse)
def doctor_login(
    request: DoctorLoginRequest,
    db: Session = Depends(get_db),
) -> DoctorTokenResponse:
    doctor_id = DoctorAuthenticationService(db).authenticate(
        request.doctorId,
        request.password.get_secret_value(),
    )
    return DoctorTokenResponse(
        access_token=create_access_token(str(doctor_id), role="doctor"),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me/appointments/today",
    response_model=list[DoctorAppointmentResponse],
)
def get_my_appointments_today(
    doctor_id: int = Depends(authenticated_doctor_id),
    db: Session = Depends(get_db),
) -> list[DoctorAppointmentResponse]:
    return AppointmentService(db).list_doctor_appointments_for_today(doctor_id)


@router.post("/doctor", dependencies=[Depends(require_doctor_password_setup_key)])
def createdoctor(
    createRequest: DoctorCreate,
    db: Session = Depends(get_db),
):
    return DoctorDirectoryService(db).createDoctor(createRequest=createRequest)


@router.post(
    "/availability",
    response_model=DoctorAvailabilityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor_availability(
    request: DoctorAvailabilityCreate,
    doctor_id: int = Depends(authenticated_doctor_id),
    db: Session = Depends(get_db),
) -> DoctorAvailabilityRead:
    """Add one recurring weekly availability slot for a doctor."""
    if request.doctorId != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors can only create their own availability",
        )
    return DoctorDirectoryService(db).create_availability(request)


@router.post(
    "/{doctor_id}/password",
    response_model=DoctorPasswordCreated,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_doctor_password_setup_key)],
)
def create_doctor_password(
    request: DoctorPasswordCreate,
    doctor_id: int = Path(gt=0),
    db: Session = Depends(get_db),
) -> DoctorPasswordCreated:
    """Set a doctor's initial password using the private setup key."""
    return DoctorDirectoryService(db).create_doctor_password(
        doctor_id=doctor_id,
        password=request.password.get_secret_value(),
    )


    

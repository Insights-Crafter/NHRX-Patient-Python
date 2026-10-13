from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from controllers.patient_controller import get_current_patient
from database.database import get_db

router = APIRouter(prefix="/patients", tags=["patients"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/me")
def get_current_patient_route(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict[str, str | int | None]:
    return get_current_patient(credentials, db)

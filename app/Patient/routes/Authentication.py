from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from Patient.schemas.AuthCredentialSchema import LoginRequest
from Patient.services.authentication import AuthenticationService
from JWT.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

authRouter = APIRouter(prefix="/auth", tags=["Auth"])


@authRouter.post("/login")
def login_route(
    login_info: LoginRequest, db: Session = Depends(get_db)
) -> dict[str, str | int]:
    patient_id = AuthenticationService(db).authenticate(
        login_info.nationalID,
        login_info.password.get_secret_value(),
    )
    return {
        "access_token": create_access_token(str(patient_id)),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

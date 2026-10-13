from sqlalchemy.orm import Session

from JWT.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from schemas.AuthCredentialSchema import LoginRequest
from services.authentication import authenticate_patient


def login_with_credentials(login_info: LoginRequest, db: Session) -> dict[str, str | int]:
    patient_id = authenticate_patient(
        db,
        login_info.nationalID,
        login_info.password.get_secret_value(),
    )
    return {
        "access_token": create_access_token(str(patient_id)),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

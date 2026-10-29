from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from JWT.jwt_handler import verify_access_token


def extract_patient_id(credentials: HTTPAuthorizationCredentials | None) -> int:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )

    try:
        claims = verify_access_token(credentials.credentials)
        patient_id = int(claims["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc

    return patient_id


def extract_doctor_id(credentials: HTTPAuthorizationCredentials | None) -> int:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = verify_access_token(credentials.credentials)
        if claims.get("role") != "doctor":
            raise ValueError("Token is not a doctor token")
        doctor_id = int(claims["sub"])
        if doctor_id <= 0:
            raise ValueError("Invalid doctor ID")
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid doctor access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return doctor_id

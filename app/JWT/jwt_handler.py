
import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY_JWT = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user_id: str, *, role: str | None = None) -> str:
    if not SECRET_KEY_JWT:
        raise RuntimeError("JWT_SECRET_KEY must be configured")
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expires_at,
    }
    if role is not None:
        payload["role"] = role

    return jwt.encode(payload, SECRET_KEY_JWT, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    if not SECRET_KEY_JWT:
        raise RuntimeError("JWT_SECRET_KEY must be configured")
    try:
        return jwt.decode(
            token,
            SECRET_KEY_JWT,
            algorithms=[ALGORITHM],
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

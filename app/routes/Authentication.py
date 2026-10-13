from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.authentication import login_with_credentials
from database.database import get_db
from schemas.AuthCredentialSchema import LoginRequest

authRouter = APIRouter(prefix="/auth", tags=["Auth"])


@authRouter.post("/login")
def login_route(
    login_info: LoginRequest, db: Session = Depends(get_db)
) -> dict[str, str | int]:
    return login_with_credentials(login_info, db)

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class LoginRequest(BaseModel):
    """Credentials accepted by POST /auth/login."""

    model_config = ConfigDict(extra="forbid")

    nationalID: str = Field(min_length=1, max_length=64)
    password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("nationalID")
    @classmethod
    def normalize_national_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("nationalID must not be blank")
        return value




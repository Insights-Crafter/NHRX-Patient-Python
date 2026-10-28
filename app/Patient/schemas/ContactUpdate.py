from pydantic import BaseModel, ConfigDict


class ContactUpdateRequest(BaseModel):
    phone :str | None = None
    email :str | None = None


class ContactUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email : str | None = None
    phone: str | None = None


class UserContactUpdateResponse(BaseModel):
    message: str
    data: ContactUpdateResponse
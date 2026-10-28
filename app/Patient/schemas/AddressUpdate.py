from pydantic import BaseModel, ConfigDict


class AddressUpdateRequest(BaseModel):
    Area:str | None = None
    HouseNumber : str | None = None
    Province : str | None = None
    City : str | None = None
    Street : str | None = None
    Block : str | None = None

class AddressUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    area: str | None
    houseNo: str | None
    province: str | None
    city: str | None
    street: str | None
    block: str | None

class UserAddressUpdateResponse(BaseModel):
    message: str
    data: AddressUpdateResponse
from pydantic import BaseModel, ConfigDict, Field


class PatientAddressCreate(BaseModel):
    patientID: int 
    Area: str = Field(min_length=5,max_length=200)
    HouseNumber: str 
    Province: str 
    City: str 
    Street: str 
    Block: str 


class PatientAddressResponse(BaseModel):
     Area: str 
     HouseNumber: str 
     Province: str 
     City: str 
     Street: str 
     Block: str 


class UserResponseAddressCreate(BaseModel):
    message : str = "Successfully Added Address"
    address : str = PatientAddressResponse
        

class PatientAddressRead(PatientAddressCreate):
    model_config = ConfigDict(from_attributes=True)

    AddressID: int

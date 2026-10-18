from pydantic import BaseModel, Field, ConfigDict


class DoctorCreate(BaseModel):
    doctorID : int = Field(min_length=1)
    Name : str 
    YearsofExperience : int
    DailyPatientLimit : int
    specialtiyID : int
    hospitalID : int

class DoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doctor_id: int
    name: str
    years_experience: int
    daily_patient_limit: int
    speciality_id: int
    hospital_id: int



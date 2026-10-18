from datetime import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Weekday = Literal[
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class DoctorAvailabilityCreate(BaseModel):
    """One recurring weekly availability slot for a doctor."""

    day: Weekday
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def end_time_must_follow_start_time(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class DoctorAvailabilityRead(DoctorAvailabilityCreate):
    model_config = ConfigDict(from_attributes=True)

    availability_id: int
    doctorID: int

from pydantic import BaseModel
from typing import Optional

class AppointmentBase(BaseModel):
    client_name: str
    date: str
    time: str
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int

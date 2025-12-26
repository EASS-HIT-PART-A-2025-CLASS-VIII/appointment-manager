"""
Pydantic + SQLModel models used for request validation,
database storage, and API responses.
"""

from typing import Optional
from sqlmodel import SQLModel, Field


class Appointment(SQLModel, table=True):
    """
    Database model for stored appointments.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str
    date: str
    time: str
    notes: Optional[str] = None


class AppointmentCreate(SQLModel):
    """
    Model for creating a new appointment.
    """

    client_name: str
    date: str
    time: str
    notes: Optional[str] = None


class AppointmentRead(SQLModel):
    """
    Model returned in API responses.
    """

    id: int
    client_name: str
    date: str
    time: str
    notes: Optional[str] = None


class AppointmentUpdate(SQLModel):
    """
    Model for updating an existing appointment.
    All fields optional.
    """

    client_name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    notes: Optional[str] = None

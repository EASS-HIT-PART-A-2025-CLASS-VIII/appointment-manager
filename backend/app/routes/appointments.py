"""
FastAPI routes exposing CRUD endpoints for appointments.
Backed by the SQLite repository.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.models import AppointmentCreate, AppointmentRead, AppointmentUpdate
from backend.app.core.deps import get_current_user
from backend.app.database import get_session
from backend.app.repository_sqlite import SQLiteAppointmentRepository

router = APIRouter(
    prefix="/appointments", dependencies=[Depends(get_current_user)]
)


def get_repo(session=Depends(get_session)):
    return SQLiteAppointmentRepository(session)


@router.get("/", response_model=list[AppointmentRead])
def list_appointments(repo=Depends(get_repo)):
    return repo.list()


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(appointment_id: int, repo=Depends(get_repo)):
    appointment = repo.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate, repo=Depends(get_repo)):
    # Prevent empty or invalid fields
    if not data.client_name.strip():
        raise HTTPException(status_code=400, detail="Client name cannot be empty")
    if not data.date.strip() or not data.time.strip():
        raise HTTPException(status_code=400, detail="Date and time are required")

    # conflict prevention
    existing = repo.find_by_datetime(data.date, data.time)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="An appointment already exists at this date and time",
        )

    return repo.create(data)


@router.put("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int, data: AppointmentUpdate, repo=Depends(get_repo)
):
    # Reject update with no fields provided
    if not any([data.client_name, data.date, data.time, data.notes]):
        raise HTTPException(status_code=400, detail="No fields provided for update")

    appointment = repo.update(appointment_id, data)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, repo=Depends(get_repo)):
    deleted = repo.delete(appointment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return

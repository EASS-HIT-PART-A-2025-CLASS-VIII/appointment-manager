from fastapi import APIRouter, HTTPException
from typing import List

from app.models import Appointment, AppointmentCreate
from app.repository import (
    get_all,
    get_by_id,
    create,
    update,
    delete
)

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

@router.get("/", response_model=List[Appointment])
def list_appointments():
    return get_all()


@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int):
    appointment = get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.post("/", response_model=Appointment)
def create_appointment(appointment_data: AppointmentCreate):
    return create(appointment_data)


@router.put("/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: int, appointment_data: AppointmentCreate):
    appointment = update(appointment_id, appointment_data)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.delete("/{appointment_id}", response_model=dict)
def delete_appointment(appointment_id: int):
    success = delete(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted"}

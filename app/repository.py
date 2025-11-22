from typing import List, Optional
from .models import Appointment, AppointmentCreate

appointments: List[Appointment] = []

_next_id = 1


def get_all() -> List[Appointment]:
    return appointments


def get_by_id(appointment_id: int) -> Optional[Appointment]:
    for appointment in appointments:
        if appointment.id == appointment_id:
            return appointment
    return None


def create(appointment_data: AppointmentCreate) -> Appointment:
    global _next_id
    new_appointment = Appointment(
        id=_next_id,
        client_name=appointment_data.client_name,
        date=appointment_data.date,
        time=appointment_data.time,
        notes=appointment_data.notes
    )
    appointments.append(new_appointment)
    _next_id += 1
    return new_appointment


def update(appointment_id: int, appointment_data: AppointmentCreate) -> Optional[Appointment]:
    appointment = get_by_id(appointment_id)
    if appointment is None:
        return None

    appointment.client_name = appointment_data.client_name
    appointment.date = appointment_data.date
    appointment.time = appointment_data.time
    appointment.notes = appointment_data.notes
    return appointment


def delete(appointment_id: int) -> bool:
    for i, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            del appointments[i]
            return True
    return False

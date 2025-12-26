from typing import Optional, List
from sqlmodel import Session, select

from app.models import (
    Appointment,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentRead,
)


class SQLiteAppointmentRepository:
    """
    Repository for managing appointments stored in a SQLite database.
    """

    def __init__(self, session: Session):
        self.session = session

    def list(self) -> List[AppointmentRead]:
        result = self.session.exec(select(Appointment)).all()
        return [AppointmentRead.model_validate(a) for a in result]

    def get(self, appointment_id: int) -> Optional[AppointmentRead]:
        appointment = self.session.get(Appointment, appointment_id)
        if appointment:
            return AppointmentRead.model_validate(appointment)
        return None

    def find_by_datetime(self, date: str, time: str) -> Optional[AppointmentRead]:
        stmt = select(Appointment).where(
            Appointment.date == date, Appointment.time == time
        )
        appointment = self.session.exec(stmt).first()
        if appointment:
            return AppointmentRead.model_validate(appointment)
        return None

    def create(self, data: AppointmentCreate) -> AppointmentRead:
        appointment = Appointment.model_validate(data)
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        return AppointmentRead.model_validate(appointment)

    def update(
        self, appointment_id: int, data: AppointmentUpdate
    ) -> Optional[AppointmentRead]:
        appointment = self.session.get(Appointment, appointment_id)
        if not appointment:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(appointment, key, value)

        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        return AppointmentRead.model_validate(appointment)

    def delete(self, appointment_id: int) -> bool:
        appointment = self.session.get(Appointment, appointment_id)
        if not appointment:
            return False

        self.session.delete(appointment)
        self.session.commit()
        return True

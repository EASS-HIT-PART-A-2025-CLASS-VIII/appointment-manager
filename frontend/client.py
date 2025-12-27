import httpx
from datetime import date

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def list_appointments():
    response = httpx.get(f"{API_BASE_URL}/appointments/")
    response.raise_for_status()
    return response.json()


def create_appointment(client_name: str, date_str: str, time_str: str, notes: str):
    payload = {
        "client_name": client_name,
        "date": date_str,
        "time": time_str,
        "notes": notes,
    }
    response = httpx.post(f"{API_BASE_URL}/appointments/", json=payload)
    response.raise_for_status()
    return response.json()


def delete_appointment(appointment_id: int):
    response = httpx.delete(f"{API_BASE_URL}/appointments/{appointment_id}")
    response.raise_for_status()


def count_appointments_today(appointments: list[dict]) -> int:
    today_str = date.today().strftime("%Y-%m-%d")
    return sum(1 for a in appointments if a["date"] == today_str)

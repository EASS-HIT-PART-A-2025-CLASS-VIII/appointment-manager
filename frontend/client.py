import httpx
from datetime import date

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def _auth_headers(token: str | None) -> dict:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def register_user(username: str, password: str) -> dict:
    payload = {"username": username, "password": password}
    response = httpx.post(f"{API_BASE_URL}/auth/register", json=payload)
    response.raise_for_status()
    return response.json()


def login_user(username: str, password: str) -> dict:
    payload = {"username": username, "password": password}
    response = httpx.post(f"{API_BASE_URL}/auth/token", data=payload)
    response.raise_for_status()
    return response.json()


def list_appointments(token: str):
    response = httpx.get(
        f"{API_BASE_URL}/appointments/", headers=_auth_headers(token)
    )
    response.raise_for_status()
    return response.json()


def create_appointment(
    token: str, client_name: str, date_str: str, time_str: str, notes: str
):
    payload = {
        "client_name": client_name,
        "date": date_str,
        "time": time_str,
        "notes": notes,
    }
    response = httpx.post(
        f"{API_BASE_URL}/appointments/",
        json=payload,
        headers=_auth_headers(token),
    )
    response.raise_for_status()
    return response.json()


def delete_appointment(token: str, appointment_id: int):
    response = httpx.delete(
        f"{API_BASE_URL}/appointments/{appointment_id}",
        headers=_auth_headers(token),
    )
    response.raise_for_status()


def export_appointments_csv(token: str) -> str:
    response = httpx.get(
        f"{API_BASE_URL}/appointments/export",
        headers=_auth_headers(token),
    )
    response.raise_for_status()
    return response.text


def request_summary(token: str) -> dict:
    response = httpx.post(
        f"{API_BASE_URL}/summary/", headers=_auth_headers(token)
    )
    response.raise_for_status()
    return response.json()


def fetch_summary_result(token: str) -> dict:
    response = httpx.get(
        f"{API_BASE_URL}/summary/result", headers=_auth_headers(token)
    )
    response.raise_for_status()
    return response.json()


def count_appointments_today(appointments: list[dict]) -> int:
    today_str = date.today().strftime("%Y-%m-%d")
    return sum(1 for a in appointments if a["date"] == today_str)

import httpx
from datetime import date
import os
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def get_headers():
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def login_user(username, password):
    response = httpx.post(
        f"{API_BASE_URL}/auth/token",
        data={"username": username, "password": password},
    )
    response.raise_for_status()
    return response.json()


def register_user(username, password):
    response = httpx.post(
        f"{API_BASE_URL}/auth/register",
        json={"username": username, "password": password},
    )
    response.raise_for_status()
    return response.json()


def list_appointments():
    response = httpx.get(f"{API_BASE_URL}/appointments/", headers=get_headers())
    response.raise_for_status()
    return response.json()


def create_appointment(client_name: str, date_str: str, time_str: str, notes: str):
    payload = {
        "client_name": client_name,
        "date": date_str,
        "time": time_str,
        "notes": notes,
    }
    response = httpx.post(f"{API_BASE_URL}/appointments/", json=payload, headers=get_headers())
    response.raise_for_status()
    return response.json()


def delete_appointment(appointment_id: int):
    response = httpx.delete(f"{API_BASE_URL}/appointments/{appointment_id}", headers=get_headers())
    response.raise_for_status()


def count_appointments_today(appointments: list[dict]) -> int:
    today_str = date.today().strftime("%Y-%m-%d")
    return sum(1 for a in appointments if a["date"] == today_str)


def request_summary():
    r = httpx.post(f"{API_BASE_URL}/summary/", headers=get_headers())
    r.raise_for_status()
    return r.json()


def fetch_summary_result():
    r = httpx.get(f"{API_BASE_URL}/summary/result", headers=get_headers())
    r.raise_for_status()
    return r.json()

import streamlit as st
import pandas as pd
from datetime import datetime

from client import (
    list_appointments,
    create_appointment,
    delete_appointment,
    count_appointments_today,
    register_user,
    login_user,
    request_summary,
    fetch_summary_result,
)


st.set_page_config(page_title="Appointment Manager", layout="wide")
st.title("📅 Appointment Dashboard")
st.caption("FastAPI backend + Streamlit interface")

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

st.subheader("Authentication")

auth_tab_login, auth_tab_register = st.tabs(["Login", "Register"])

with auth_tab_login:
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input(
            "Password", type="password", key="login_password"
        )
        login_submit = st.form_submit_button("Login")

    if login_submit:
        try:
            token = login_user(login_username, login_password)["access_token"]
            st.session_state["auth_token"] = token
            st.success("Logged in successfully.")
            st.rerun()
        except Exception as exc:
            st.error(f"Login failed: {exc}")

with auth_tab_register:
    with st.form("register_form"):
        register_username = st.text_input("Username", key="register_username")
        register_password = st.text_input(
            "Password", type="password", key="register_password"
        )
        register_submit = st.form_submit_button("Register")

    if register_submit:
        try:
            token = register_user(register_username, register_password)[
                "access_token"
            ]
            st.session_state["auth_token"] = token
            st.success("Registration successful.")
            st.rerun()
        except Exception as exc:
            st.error(f"Registration failed: {exc}")

if not st.session_state.get("auth_token"):
    st.info("Please login or register to continue.")
    st.stop()

auth_token = st.session_state["auth_token"]


# Load appointments with caching
@st.cache_data(ttl=10)
def load_data(token: str):
    return list_appointments(token)


# -----------------------------
# Section 1: Metrics
# -----------------------------
appointments = load_data(auth_token)

total_count = len(appointments)
today_count = count_appointments_today(appointments)

col1, col2 = st.columns(2)
col1.metric("Total Appointments", total_count)
col2.metric("Today's Appointments", today_count)


# -----------------------------
# Section 2: Appointment Table
# -----------------------------
st.subheader("All Appointments")

if total_count == 0:
    st.info("No appointments yet.")
else:
    df = pd.DataFrame(appointments)
    st.dataframe(df, use_container_width=True)


# Refresh button
if st.button("Refresh Data"):
    load_data.clear()
    st.rerun()


# -----------------------------
# Section 3: Create Appointment
# -----------------------------
st.subheader("Create New Appointment")

with st.form("create_form"):
    client_name = st.text_input("Client Name")
    date_str = st.date_input("Date", datetime.today()).strftime("%Y-%m-%d")
    time_str = st.time_input("Time").strftime("%H:%M")
    notes = st.text_input("Notes", "")

    submitted = st.form_submit_button("Create Appointment")

if submitted:
    try:
        create_appointment(auth_token, client_name, date_str, time_str, notes)
        load_data.clear()
        st.success("Appointment created successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")


# -----------------------------
# Section 4: Delete Appointment
# -----------------------------
st.subheader("Delete Appointment")

if total_count > 0:
    ids = [a["id"] for a in appointments]
    selected = st.selectbox("Select ID to delete", ids)

    if st.button("Delete Selected"):
        try:
            delete_appointment(auth_token, int(selected))
            load_data.clear()
            st.success("Appointment deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")


# -----------------------------
# Section 5: AI Summary Generator
# -----------------------------
st.subheader("AI Summary Generator")

colA, colB = st.columns(2)

with colA:
    if st.button("Generate AI Summary"):
        try:
            resp = request_summary(auth_token)
            st.success(f"Summary job queued! ({resp['count']} appointments)")
        except Exception as e:
            st.error(f"Error: {e}")

with colB:
    if st.button("Fetch Summary Result"):
        try:
            result = fetch_summary_result(auth_token)
            if result["status"] == "pending":
                st.warning("Summary not ready yet, try again in a few seconds.")
            else:
                st.success("Summary Ready:")
                st.write(result["summary"])
        except Exception as e:
            st.error(f"Error: {e}")

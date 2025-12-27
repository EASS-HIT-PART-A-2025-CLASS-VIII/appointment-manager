import streamlit as st
import pandas as pd
from datetime import datetime

from client import (
    list_appointments,
    create_appointment,
    delete_appointment,
    count_appointments_today,
)

st.set_page_config(page_title="Appointment Manager", layout="wide")
st.title("📅 Appointment Dashboard")
st.caption("FastAPI backend + Streamlit interface")


# Load appointments with caching
@st.cache_data(ttl=10)
def load_data():
    return list_appointments()


# -----------------------------
# Section 1: Metrics
# -----------------------------
appointments = load_data()

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
        create_appointment(client_name, date_str, time_str, notes)
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
            delete_appointment(int(selected))
            load_data.clear()
            st.success("Appointment deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

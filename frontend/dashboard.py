import streamlit as st
import pandas as pd
from datetime import datetime
import time

from client import (
    list_appointments,
    create_appointment,
    delete_appointment,
    count_appointments_today,
    request_summary,
    fetch_summary_result,
    login_user,
    register_user,
)

st.set_page_config(page_title="Appointment Manager", layout="wide")

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "page" not in st.session_state:
    st.session_state.page = "login"


def show_login_page():
    st.title("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                data = login_user(username, password)
                st.session_state.access_token = data["access_token"]
                st.session_state.page = "dashboard"
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")
    
    if st.button("Go to Register"):
        st.session_state.page = "register"
        st.rerun()


def show_register_page():
    st.title("📝 Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    data = register_user(username, password)
                    st.session_state.access_token = data["access_token"]
                    st.session_state.page = "dashboard"
                    st.success("Registered successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {e}")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


def show_dashboard():
    st.title("📅 Appointment Dashboard")
    
    if st.button("Logout"):
        st.session_state.access_token = None
        st.session_state.page = "login"
        st.rerun()

    # Load appointments with caching
    # Note: We might want to remove caching or key it by user if multi-user support is needed
    # For now, we'll just call the API directly to ensure freshness
    try:
        appointments = list_appointments()
    except Exception as e:
        st.error(f"Failed to load appointments: {e}")
        appointments = []

    # -----------------------------
    # Section 1: Metrics
    # -----------------------------
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
                resp = request_summary()
                st.success(f"Summary job queued! ({resp['count']} appointments)")
            except Exception as e:
                st.error(f"Error: {e}")

    with colB:
        if st.button("Fetch Summary Result"):
            try:
                result = fetch_summary_result()
                if result["status"] == "pending":
                    st.warning("Summary not ready yet, try again in a few seconds.")
                else:
                    st.success("Summary Ready:")
                    st.write(result["summary"])
            except Exception as e:
                st.error(f"Error: {e}")


# Main routing logic
if st.session_state.access_token:
    show_dashboard()
elif st.session_state.page == "register":
    show_register_page()
else:
    show_login_page()

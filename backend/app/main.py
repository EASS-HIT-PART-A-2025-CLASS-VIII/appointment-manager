"""
Main FastAPI application entrypoint.
Includes routers and defines the root endpoint.
"""

from fastapi import FastAPI
from backend.app.database import init_db
from backend.app.routes.appointments import router


app = FastAPI(title="Appointment Manager")

# Attach routers
app.include_router(router)


# Root endpoint
@app.get("/")
def root():
    return {"status": "ok", "message": "Appointments API is running"}


# Initialize DB tables
init_db()

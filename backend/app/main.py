"""
Main FastAPI application entrypoint.
Includes routers and defines the root endpoint.
"""

from fastapi import FastAPI
from backend.app.database import init_db
from backend.app.routes.appointments import router
from backend.app.routes.summary import router as summary_router

app = FastAPI(title="Appointment Manager")

# Attach routers
app.include_router(router)
app.include_router(summary_router)

# Root endpoint
@app.get("/")
def root():
    return {"status": "ok", "message": "Appointments API is running"}


@app.on_event("startup")
def on_startup():
    init_db()

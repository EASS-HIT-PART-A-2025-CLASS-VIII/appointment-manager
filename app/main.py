from fastapi import FastAPI
from app.routes.appointments import router as appointments_router

app = FastAPI()

app.include_router(appointments_router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Appointments API is running"}

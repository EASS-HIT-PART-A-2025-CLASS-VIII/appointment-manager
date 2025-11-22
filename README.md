# Appointment Manager – FastAPI Backend (EX1)

A lightweight **FastAPI** microservice that manages appointments.  
This is the backend foundation for the full project (EX1 → EX2 → EX3), following the requirements from Sessions 02–04.

The service exposes full CRUD operations, uses **Pydantic** models, an **in-memory repository**, and includes a **Dockerized runtime** as required for EX1 preparation toward the full multi-service system.

---

## Project Structure

```
appointments-api/
│
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── models.py            # Pydantic data models
│   ├── repository.py        # In-memory persistence layer
│   ├── routes/
│   │   └── appointments.py  # CRUD endpoints router
│   └── __init__.py
│
├── tests/
│   └── test_appointments.py # Pytest suite (happy-path coverage)
│
├── requirements.txt
├── Dockerfile
├── pytest.ini
└── README.md
```

---

## Run the API with Docker (Recommended & Required for EX1)

### 1️⃣ Build the image
```powershell
docker build -t appointments-api .
```

### 2️⃣ Run the container
```powershell
docker run --rm -p 8000:8000 appointments-api
```

### 3️⃣ Open the interactive API docs
```
http://localhost:8000/docs
```

---

## Running Tests (Locally or Inside CI)

```
pytest -q
```

The test suite covers:

- Creating a new appointment  
- Listing all appointments  
- Retrieving a specific appointment  
- Updating appointment details  
- Deleting an appointment and verifying deletion  

Expected output:
```
5 passed in X.XXs
```

---

## API Endpoints Overview

| Method | Path                  | Description                       |
|--------|-----------------------|-----------------------------------|
| POST   | `/appointments/`      | Create a new appointment          |
| GET    | `/appointments/`      | List all appointments             |
| GET    | `/appointments/{id}`  | Retrieve appointment by ID        |
| PUT    | `/appointments/{id}`  | Update an existing appointment    |
| DELETE | `/appointments/{id}`  | Delete an appointment             |

### Example payload (POST)
```json
{
  "client_name": "John Doe",
  "date": "2025-01-01",
  "time": "12:00",
  "notes": "Consultation"
}
```

---

## Notes

- Persistence is **in-memory** only (per EX1 specification).  
- IDs are auto-incrementing integers starting from 1.  
- A real SQLite/SQLModel persistence layer will be added in EX2/EX3.  
- This backend is the foundation for the interface layer and future multi-service architecture.



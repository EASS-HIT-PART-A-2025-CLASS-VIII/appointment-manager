# Appointment Manager – Full System (Backend + Frontend + Docker Compose)

A complete appointment-management system built across two project stages:

- **EX1:** FastAPI backend (CRUD API + tests + Docker)
- **EX2:** Streamlit dashboard frontend + Docker + Docker Compose

The system includes:

- A **FastAPI backend** using **SQLite + SQLModel**
- A **Streamlit frontend** communicating with the API
- A **Docker Compose** setup that runs both services together

---

## Project Structure

```
appointments-api/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── repository.py
│   │   ├── repository_sqlite.py
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── appointments.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_appointments.py
│   │
│   └── Dockerfile
│
├── frontend/
│   ├── client.py
│   ├── dashboard.py
│   └── Dockerfile
│
├── data/
│   └── appointments.db     # SQLite DB (ignored in Git)
│
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## API Endpoints Overview

| Method | Path                     | Description                                 |
|--------|---------------------------|---------------------------------------------|
| **GET**    | `/`                       | Root endpoint – service health message       |
| **POST**   | `/auth/register`          | Register a new user and return JWT           |
| **POST**   | `/auth/token`             | Login and return JWT                         |
| **POST**   | `/appointments/`          | Create a new appointment                     |
| **GET**    | `/appointments/`          | List all appointments                        |
| **GET**    | `/appointments/{id}`      | Retrieve appointment by ID                   |
| **PUT**    | `/appointments/{id}`      | Update an existing appointment               |
| **DELETE** | `/appointments/{id}`      | Delete an appointment                        |

---

# Running the System with Docker Compose (Recommended)

### 1️⃣ Build all services
```bash
docker compose build
```

### 2️⃣ Run backend + frontend
```bash
docker compose up
```

The backend requires a JWT secret. You can supply it via an .env file or inline:

```bash
JWT_SECRET_KEY="change-me" docker compose up
```

### 3️⃣ Access the system

| Component | URL |
|----------|-----|
| **Frontend (Streamlit UI)** | http://localhost:8501 |
| **Backend API Docs** | http://localhost:8000/docs |

---

# Running Backend Alone (EX1)

### Build backend image
```bash
docker build -t appointments-api-backend ./backend
```

### Run backend
```bash
docker run -p 8000:8000 appointments-api-backend
```

### API docs
```
http://localhost:8000/docs
```

---

# Running Tests

```bash
pytest -q
```

Tests cover:

- Create
- Read all
- Read single
- Update
- Delete + verify deletion

Example expected output:

```
5 passed in X.XXs
```

---

# Running Frontend Alone (EX2)

### Build frontend image
```bash
docker build -t appointments-api-frontend ./frontend
```

### Run frontend (pointing to backend)
```bash
docker run -p 8501:8501 -e API_BASE_URL="http://127.0.0.1:8000" appointments-api-frontend
```

---

# 📝 Notes

- Backend uses **SQLite + SQLModel** (persistent storage)
- Auth uses JWT; protected endpoints require `Authorization: Bearer <token>`
- Frontend communicates via **httpx**
- Docker Compose links backend + frontend on an internal network (`backend:8000`)
- SQLite DB file (`data/appointments.db`) is **excluded from Git**
- Root endpoint (`GET /`) added for basic service health verification



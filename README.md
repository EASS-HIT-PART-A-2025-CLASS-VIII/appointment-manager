# Appointment Manager – Full System (Backend + Frontend + Redis Worker + JWT + Docker Compose)

A complete appointment-management system built across three project stages:

- **EX1:** FastAPI backend (CRUD API + tests + Docker)
- **EX2:** Streamlit dashboard frontend + Docker + Docker Compose
- **EX3:** Redis-backed AI worker, JWT auth, and CSV export

The system includes:

- A **FastAPI backend** using **SQLite + SQLModel**
- A **Streamlit frontend** communicating with the API
- A **Redis-backed AI summary worker** that processes background jobs
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
│   │   ├── core/
│   │   │   ├── deps.py
│   │   │   └── security.py
│   │   ├── database.py
│   │   ├── repository.py
│   │   ├── repository_sqlite.py
│   │   ├── __init__.py
│   │   ├── workers/
│   │   │   └── summary_worker.py
│   │   └── routes/
│   │       ├── appointments.py
│   │       ├── auth.py
│   │       └── summary.py
│   │
│   │   ├── scripts/
│   │   │   ├── refresh.py
│   │   │   └── demo.sh
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_appointments.py
│   │   └── test_auth.py
│   │   ├── test_summary.py
│   │   └── test_summary_worker.py
│   │   └── test_refresh.py
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
├── docs/
│   ├── EX3-notes.md
│   └── runbooks/
│       └── compose.md
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
| **POST**   | `/summary/`               | Queue AI summary job (auth required)         |
| **GET**    | `/summary/result`         | Fetch latest summary (auth required)         |
| **POST**   | `/appointments/`          | Create a new appointment                     |
| **GET**    | `/appointments/`          | List all appointments                        |
| **GET**    | `/appointments/export`    | Export appointments as CSV (auth required)   |
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

The AI summary worker requires a Gemini key (used inside the worker container):

```bash
GOOGLE_API_KEY="your-key" GOOGLE_MODEL="google-gla:gemini-2.5-flash" docker compose up
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

Note: `test_refresh.py` uses Redis and will skip if Redis is not running.

Tests cover:

- Create
- Read all
- Read single
- Update
- Delete + verify deletion
- Validation errors (empty fields, conflicts, empty update)
- Auth register/login
- Auth rejects invalid credentials/token
- Auth rejects expired token
- Protected endpoints require JWT
- Summary queue/result behavior (Redis mocked)
- Summary worker prompt formatting and processing (Agent mocked)
- Async refresh idempotency (Redis-backed)
- CSV export output

Example expected output:

```
23 passed, 1 skipped in X.XXs
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

# EX3 Docs and Scripts

- Architecture and security notes: docs/EX3-notes.md
- Compose runbook: docs/runbooks/compose.md (uses docker-compose.yml)
- Async refresher: backend/scripts/refresh.py
- Demo walkthrough: backend/scripts/demo.sh

---

# 📝 Notes

- Backend uses **SQLite + SQLModel** (persistent storage)
- Auth uses JWT; protected endpoints require `Authorization: Bearer <token>`
- Summary jobs are queued in Redis and processed by the background worker
- Frontend communicates via **httpx**
- Docker Compose links backend + frontend on an internal network (`backend:8000`)
- SQLite DB file (`data/appointments.db`) is **excluded from Git**
- Root endpoint (`GET /`) added for basic service health verification



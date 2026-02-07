# EX3 Project Notes: Appointment Manager

This document summarizes the EX3 architecture, security, and orchestration for the Appointment Manager project.

---

## 1. Project Overview
The project evolved from a FastAPI CRUD service (EX1) and a Streamlit interface (EX2) into a local microservices stack (EX3) with an async AI summary worker, JWT authentication, and CSV export.

---

## 2. Service Architecture and Orchestration
Docker Compose orchestrates four cooperating services:

| Service | Role | Key Tech |
| --- | --- | --- |
| Backend | API logic and persistence | FastAPI, SQLModel |
| Frontend | User interface | Streamlit |
| Worker | Async AI summaries | Python, Pydantic AI |
| Redis | Task queue and idempotency | Redis 7 |

### Persistence
SQLite is used for appointments and users. The database is stored in `./data` and mounted into the backend container so data persists across restarts.

---

## 3. Async Refresher and Idempotency (Session 09)
The async refresher script is implemented in `backend/scripts/refresh.py`.

- **Bounded concurrency**: uses an asyncio semaphore.
- **Retries**: exponential backoff (up to 3 attempts).
- **Idempotency**: Redis keys prevent reprocessing (`refresh_lock:summary:<label>`).

### Redis Trace Excerpt (Example)
```text
[REDIS] SETEX refresh_lock:summary:daily 300 done
[BACKEND] POST /summary/ 200
[WORKER] Summary generated for 3 appointments
```

---

## 4. Security Baseline (Session 11)
- **Hashed credentials**: Bcrypt password hashing.
- **JWT authentication**: bearer tokens for protected routes.
- **Role checks**: admin-only route `/auth/admin/ping` requires `role=admin`.

### Secret Rotation Steps
1. Generate a new secret string (32+ chars).
2. Update `JWT_SECRET_KEY` in your `.env` or environment.
3. Restart services with `docker compose up -d`.
4. Existing tokens are invalidated and users must re-login.

---

## 5. Enhancement
CSV export is available at `/appointments/export` and in the UI download button. Tests cover the CSV output format.

---

## 6. Automated Tests
Tests cover CRUD, validation, auth, role checks, summary queue behavior, worker processing, and CSV export. See `backend/tests` for details.

---

## 7. Local Demo
Run the demo script:

```bash
./backend/scripts/demo.sh
```

It starts the stack, registers a user, creates an appointment, downloads CSV, and queues a summary job.

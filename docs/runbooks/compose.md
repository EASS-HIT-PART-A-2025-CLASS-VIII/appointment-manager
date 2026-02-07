# Compose Runbook

This document explains how to run the stack locally and verify the services.

---

## 1. Launching the Stack
Build and start all services (backend, frontend, worker, Redis):

```bash
docker compose up -d --build
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- Redis: localhost:6379

---

## 2. Health Checks
Check container status:

```bash
docker compose ps
```

Verify the backend is responding:

```bash
curl -I http://localhost:8000/
```

---

## 3. Worker Logs
Follow worker logs to confirm summary processing:

```bash
docker compose logs -f worker
```

---

## 4. Rate-Limit Headers
Rate-limit headers are not currently implemented. If you add a limiter later, verify headers with:

```bash
curl -I http://localhost:8000/appointments/
```

---

## 5. Automated Validation
Run tests inside the backend container:

```bash
docker compose exec backend pytest -q
```

OpenAPI contract checks (requires Schemathesis installed in the backend image):

```bash
docker compose run --rm backend schemathesis run http://backend:8000/openapi.json
```

#!/usr/bin/env bash
set -euo pipefail

if [ -z "${JWT_SECRET_KEY:-}" ]; then
  echo "JWT_SECRET_KEY is not set. Provide it in .env or the shell."
  exit 1
fi

if [ -z "${GOOGLE_API_KEY:-}" ]; then
  echo "GOOGLE_API_KEY is not set. The worker will not generate AI summaries."
fi

echo "Starting services..."
docker compose up -d --build

sleep 3

echo "Registering user..."
REGISTER=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo"}')

TOKEN=$(python - <<'PY'
import json, sys
print(json.loads(sys.argv[1])["access_token"])
PY
"$REGISTER")

if [ -z "$TOKEN" ]; then
  echo "Registration failed."
  exit 1
fi

AUTH="Authorization: Bearer $TOKEN"

echo "Creating appointment..."
curl -s -X POST http://localhost:8000/appointments/ \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"client_name":"Demo User","date":"2026-02-07","time":"10:00","notes":"demo"}'

echo

echo "Exporting CSV..."
curl -s http://localhost:8000/appointments/export -H "$AUTH" > /tmp/appointments.csv
ls -l /tmp/appointments.csv

echo "Queueing summary job..."
curl -s -X POST http://localhost:8000/summary/ -H "$AUTH"

echo

echo "Frontend: http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"

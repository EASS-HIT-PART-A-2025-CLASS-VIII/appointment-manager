#!/usr/bin/env bash
set -euo pipefail

echo "=== Appointment Manager Demo ==="

if [ -z "${JWT_SECRET_KEY:-}" ]; then
  echo "JWT_SECRET_KEY is not set! Export it before running."
  exit 1
fi

if [ -z "${GOOGLE_API_KEY:-}" ]; then
  echo "GOOGLE_API_KEY missing — AI summaries will NOT work."
fi

echo "Starting Docker Compose..."
docker compose up -d --build

echo "Waiting for backend to start..."
for i in 1 2 3 4 5; do
  if curl -s -o /dev/null http://localhost:8000/; then
    break
  fi
  sleep 2
done

USERNAME="demo"
PASSWORD="demo"
DATE_STR=$(date +"%Y-%m-%d")
TIME_STR=$(date +"%H:%M:%S")

extract_token() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("access_token", ""))
except Exception:
    print("")
PY
  elif command -v python >/dev/null 2>&1; then
    python - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("access_token", ""))
except Exception:
    print("")
PY
  else
    printf '%s' "$1" | sed -n 's/.*"access_token"[ ]*:[ ]*"\([^"]*\)".*/\1/p'
  fi
}

extract_status() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("status", ""))
except Exception:
    print("")
PY
  elif command -v python >/dev/null 2>&1; then
    python - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("status", ""))
except Exception:
    print("")
PY
  else
    printf '%s' "$1" | sed -n 's/.*"status"[ ]*:[ ]*"\([^"]*\)".*/\1/p'
  fi
}

print_summary() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("summary", data))
except Exception:
    print(sys.argv[1])
PY
  elif command -v python >/dev/null 2>&1; then
    python - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("summary", data))
except Exception:
    print(sys.argv[1])
PY
  else
    printf '%s\n' "$1"
  fi
}

extract_id() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("id", ""))
except Exception:
    print("")
PY
  elif command -v python >/dev/null 2>&1; then
    python - <<'PY' "$1"
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get("id", ""))
except Exception:
    print("")
PY
  else
    printf '%s' "$1" | sed -n 's/.*"id"[ ]*:[ ]*\([0-9]*\).*/\1/p'
  fi
}

echo "Registering user ($USERNAME)..."
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

REGISTER_BODY=$(printf '%s' "$REGISTER_RESPONSE" | sed '$d')
REGISTER_CODE=$(printf '%s' "$REGISTER_RESPONSE" | tail -n 1)

TOKEN=""
if [ "$REGISTER_CODE" = "200" ]; then
  TOKEN=$(extract_token "$REGISTER_BODY")
else
  echo "User already exists or register failed (HTTP $REGISTER_CODE) — logging in..."
  LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST http://localhost:8000/auth/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$USERNAME&password=$PASSWORD")

  LOGIN_BODY=$(printf '%s' "$LOGIN_RESPONSE" | sed '$d')
  LOGIN_CODE=$(printf '%s' "$LOGIN_RESPONSE" | tail -n 1)

  if [ "$LOGIN_CODE" = "200" ]; then
    TOKEN=$(extract_token "$LOGIN_BODY")
  fi
fi

if [ -z "$TOKEN" ]; then
  echo "ERROR: Could not obtain JWT token (register & login failed)"
  exit 1
fi

echo "✔ Token acquired."
AUTH="Authorization: Bearer $TOKEN"

echo "Creating example appointment..."
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/appointments/ \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d "{\"client_name\":\"Demo User\",\"date\":\"$DATE_STR\",\"time\":\"$TIME_STR\",\"notes\":\"demo\"}")

CREATE_BODY=$(printf '%s' "$CREATE_RESPONSE" | sed '$d')
CREATE_CODE=$(printf '%s' "$CREATE_RESPONSE" | tail -n 1)

if [ "$CREATE_CODE" != "200" ] && [ "$CREATE_CODE" != "201" ]; then
  echo "ERROR: Create appointment failed (HTTP $CREATE_CODE)."
  echo "$CREATE_BODY"
  exit 1
fi

APPT_ID=$(extract_id "$CREATE_BODY")

if [ -z "$APPT_ID" ]; then
  echo "ERROR: Could not parse appointment id."
  exit 1
fi

echo "Created appointment id: $APPT_ID"

echo "Listing appointments..."
curl -s http://localhost:8000/appointments/ -H "$AUTH"

echo
echo "Updating appointment..."
curl -s -X PUT http://localhost:8000/appointments/$APPT_ID \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"notes":"updated"}'

echo
echo "Fetching updated appointment..."
curl -s http://localhost:8000/appointments/$APPT_ID -H "$AUTH"

echo
echo "Exporting appointments to CSV..."
curl -s http://localhost:8000/appointments/export -H "$AUTH" > /tmp/appointments.csv
echo "✔ CSV exported to: /tmp/appointments.csv"
ls -l /tmp/appointments.csv
echo "CSV contents:"
cat /tmp/appointments.csv

echo
echo "Queuing AI summary job..."
curl -s -X POST http://localhost:8000/summary/ -H "$AUTH"

echo
echo "Waiting for worker to process summary..."
SUMMARY_PAYLOAD=""
for attempt in 1 2 3 4 5; do
  sleep 2
  SUMMARY_PAYLOAD=$(curl -s http://localhost:8000/summary/result -H "$AUTH")
  STATUS=$(extract_status "$SUMMARY_PAYLOAD")

  if [ "$STATUS" = "ready" ]; then
    break
  fi
done

echo
echo "=== AI SUMMARY OUTPUT ==="
print_summary "$SUMMARY_PAYLOAD"
echo "=========================="

echo
echo "Deleting appointment..."
curl -s -X DELETE http://localhost:8000/appointments/$APPT_ID -H "$AUTH"

echo
echo "Frontend:  http://localhost:8501"
echo "API Docs:  http://localhost:8000/docs"
echo "Demo complete ✔"

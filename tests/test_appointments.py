from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_appointment():
    response = client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["client_name"] == "Test User"


def test_get_appointments():
    response = client.get("/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_single_appointment():
    response = client.get("/appointments/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1


def test_update_appointment():
    response = client.put(
        "/appointments/1",
        json={
            "client_name": "Updated User",
            "date": "2025-01-01",
            "time": "13:00",
            "notes": "Updated",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["client_name"] == "Updated User"


def test_delete_appointment():
    response = client.delete("/appointments/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Appointment deleted"

    # Verify delete
    response = client.get("/appointments/1")
    assert response.status_code == 404

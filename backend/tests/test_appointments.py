from fastapi.testclient import TestClient
from backend.app.main import app

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
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["client_name"] == "Test User"


def test_get_appointments():
    # create an appointment
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
    )

    response = client.get("/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_single_appointment():
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
    )

    response = client.get("/appointments/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_update_appointment():
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
    )

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
    assert response.json()["client_name"] == "Updated User"


def test_delete_appointment():
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
    )

    response = client.delete("/appointments/1")
    assert response.status_code == 204
    assert response.text == ""

    # Verify delete
    response = client.get("/appointments/1")
    assert response.status_code == 404

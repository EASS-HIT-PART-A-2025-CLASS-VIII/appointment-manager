def test_create_appointment(client, auth_headers):
    response = client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["client_name"] == "Test User"


def test_create_appointment_rejects_empty_name(client, auth_headers):
    response = client.post(
        "/appointments/",
        json={
            "client_name": " ",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_get_appointments(client, auth_headers):
    # create an appointment
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )

    response = client.get("/appointments/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_single_appointment(client, auth_headers):
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )

    response = client.get("/appointments/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_create_appointment_conflict(client, auth_headers):
    client.post(
        "/appointments/",
        json={
            "client_name": "User One",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "First",
        },
        headers=auth_headers,
    )

    response = client.post(
        "/appointments/",
        json={
            "client_name": "User Two",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Second",
        },
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_update_appointment(client, auth_headers):
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )

    response = client.put(
        "/appointments/1",
        json={
            "client_name": "Updated User",
            "date": "2025-01-01",
            "time": "13:00",
            "notes": "Updated",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["client_name"] == "Updated User"


def test_update_appointment_with_no_fields_fails(client, auth_headers):
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )

    response = client.put("/appointments/1", json={}, headers=auth_headers)
    assert response.status_code == 400


def test_delete_appointment(client, auth_headers):
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )

    response = client.delete("/appointments/1", headers=auth_headers)
    assert response.status_code == 204
    assert response.text == ""

    # Verify delete
    response = client.get("/appointments/1", headers=auth_headers)
    assert response.status_code == 404


def test_export_appointments_csv(client, auth_headers):
    client.post(
        "/appointments/",
        json={
            "client_name": "Test User",
            "date": "2025-01-01",
            "time": "12:00",
            "notes": "Testing",
        },
        headers=auth_headers,
    )

    response = client.get("/appointments/export", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    body = response.text.splitlines()
    assert body[0] == "id,client_name,date,time,notes"
    assert "Test User" in body[1]

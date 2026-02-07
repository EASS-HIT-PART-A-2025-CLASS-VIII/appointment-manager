from backend.app.core.security import get_password_hash
from backend.app.models import User


def test_register_returns_token(client):
    response = client.post(
        "/auth/register",
        json={"username": "alice", "password": "secret"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_returns_token(client):
    client.post(
        "/auth/register",
        json={"username": "bob", "password": "secret"},
    )

    response = client.post(
        "/auth/token",
        data={"username": "bob", "password": "secret"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_register_duplicate_user_fails(client):
    response = client.post(
        "/auth/register",
        json={"username": "duplicate", "password": "secret"},
    )
    assert response.status_code == 200

    response = client.post(
        "/auth/register",
        json={"username": "duplicate", "password": "secret"},
    )
    assert response.status_code == 400


def test_login_with_bad_password_fails(client):
    client.post(
        "/auth/register",
        json={"username": "badpass", "password": "secret"},
    )

    response = client.post(
        "/auth/token",
        data={"username": "badpass", "password": "wrong"},
    )
    assert response.status_code == 400


def test_protected_endpoints_require_auth(client):
    response = client.get("/appointments/")
    assert response.status_code == 401

    response = client.get("/summary/result")
    assert response.status_code == 401


def test_protected_endpoints_reject_invalid_token(client):
    headers = {"Authorization": "Bearer invalid.token.value"}

    response = client.get("/appointments/", headers=headers)
    assert response.status_code == 401


def test_protected_endpoints_reject_expired_token(client):
    client.post(
        "/auth/register",
        json={"username": "expired", "password": "secret"},
    )

    from datetime import datetime, timedelta, timezone
    from jose import jwt

    from backend.app.core.security import ALGORITHM, SECRET_KEY

    expired = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = jwt.encode(
        {"sub": "expired", "exp": expired}, SECRET_KEY, algorithm=ALGORITHM
    )

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/appointments/", headers=headers)
    assert response.status_code == 401


def test_admin_route_requires_admin_role(client, session):
    user = User(
        username="admin",
        hashed_password=get_password_hash("secret"),
        role="admin",
    )
    session.add(user)
    session.commit()

    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "secret"},
    )
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/admin/ping", headers=headers)
    assert response.status_code == 200


def test_admin_route_rejects_non_admin(client):
    response = client.post(
        "/auth/register",
        json={"username": "user", "password": "secret"},
    )
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/admin/ping", headers=headers)
    assert response.status_code == 403

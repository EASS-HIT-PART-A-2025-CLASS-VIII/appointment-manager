import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("GOOGLE_API_KEY", "test-key")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

from backend.app.main import app
from backend.app.database import get_session


TEST_DB = "appointments_test.db"


@pytest.fixture
def session():
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            pass

    engine = create_engine(
        f"sqlite:///{TEST_DB}", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            pass


@pytest.fixture(autouse=True)
def override_session(session):
    def override():
        yield session

    app.dependency_overrides[get_session] = override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "password": "testpass"},
    )
    if response.status_code == 400:
        response = client.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass"},
        )

    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

import os
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

"""
Database engine and session utilities for SQLite persistence.
"""

from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = "sqlite:///data/appointments.db"

engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def init_db():
    from backend.app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

import os

# Point the app at an isolated SQLite file before any app module is imported.
os.environ["DATABASE_URL"] = "sqlite:///./test_sentinel.db"
os.environ["JWT_SECRET"] = "test-secret-key-for-pytest-only-32b"
os.environ["SEED_ADMIN_EMAIL"] = "admin@test.local"
os.environ["SEED_ADMIN_PASSWORD"] = "AdminPass123!"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.seed import seed

engine = create_engine(
    "sqlite://",  # in-memory, shared across connections via StaticPool
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def seed_database(setup_database):
    # Seed via the app's own seed function, but against the test engine.
    import app.seed as seed_module

    original = seed_module.SessionLocal
    seed_module.SessionLocal = TestingSessionLocal
    try:
        seed_module.seed()
    finally:
        seed_module.SessionLocal = original


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def admin_tokens(client) -> dict:
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@test.local",
        "password": "AdminPass123!",
    })
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture(scope="session")
def admin_headers(admin_tokens) -> dict:
    return {"Authorization": f"Bearer {admin_tokens['access_token']}"}

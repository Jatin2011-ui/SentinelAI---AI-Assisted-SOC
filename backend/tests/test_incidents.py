"""Tests for incident correlation."""
from fastapi.testclient import TestClient
from tests.conftest import client

def test_correlate_creates_incident(client: TestClient):
    for _ in range(3):
        client.post("/api/v1/events", json={
            "timestamp": "2026-09-04T02:13:25Z",
            "event_type": "authentication_failure",
            "source": "auth",
            "username": "carol",
            "source_ip": "5.6.7.8",
        })
    resp = client.post("/api/v1/incidents/correlate?window_minutes=30&min_events=3")
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] >= 1
    incidents = client.get("/api/v1/incidents").json()
    assert len(incidents) >= 1

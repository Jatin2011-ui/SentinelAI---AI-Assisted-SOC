"""Tests for event ingestion pipeline."""
from fastapi.testclient import TestClient
from app.main import app
from tests.conftest import client

def test_ingest_event(client: TestClient):
    payload = {
        "timestamp": "2026-09-04T02:13:25Z",
        "source": "firewall",
        "event_type": "authentication_failure",
        "source_ip": "192.168.1.10",
        "destination_ip": "192.168.1.20",
        "username": "admin",
        "severity": "MEDIUM",
        "raw_message": "Failed SSH authentication"
    }
    resp = client.post("/api/v1/events", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["event_type"] == "authentication_failure"
    assert data["source_ip"] == "192.168.1.10"
    assert "event_id" in data

def test_list_events(client: TestClient):
    # create two events
    for et in ["authentication_failure", "process_creation"]:
        client.post("/api/v1/events", json={
            "timestamp": "2026-09-04T02:13:25Z",
            "event_type": et,
            "source": "test",
        })
    resp = client.get("/api/v1/events")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 2

def test_get_event_by_id(client: TestClient):
    resp = client.post("/api/v1/events", json={
        "timestamp": "2026-09-04T02:13:25Z",
        "event_type": "dns_request",
        "source": "ids",
    })
    event_id = resp.json()["event_id"]
    resp2 = client.get(f"/api/v1/events/{event_id}")
    assert resp2.status_code == 200
    assert resp2.json()["event_id"] == event_id

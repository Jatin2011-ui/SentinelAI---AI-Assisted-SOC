"""Tests for supervisor agent."""
from fastapi.testclient import TestClient
from tests.conftest import client

def test_supervisor_investigate(client: TestClient):
    # create incident
    for _ in range(3):
        client.post("/api/v1/events", json={
            "timestamp": "2026-09-04T02:13:25Z",
            "event_type": "authentication_failure",
            "source": "auth",
            "username": "eve",
            "source_ip": "1.1.1.1",
        })
    corr = client.post("/api/v1/incidents/correlate?window_minutes=30&min_events=3")
    inc_id = corr.json()["incidents"][0]
    resp = client.post(f"/api/v1/incidents/{inc_id}/investigate")
    assert resp.status_code == 200
    state = resp.json()["state"]
    assert state["incident_id"] == inc_id
    assert "Supervisor: start investigation plan" in state["investigation_history"]

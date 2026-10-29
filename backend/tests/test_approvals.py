"""Tests for the approval workflow (RBAC-protected)."""
from fastapi.testclient import TestClient
from tests.conftest import client


def _make_incident(client: TestClient) -> str:
    for _ in range(3):
        client.post("/api/v1/events", json={
            "timestamp": "2026-09-04T02:13:25Z",
            "event_type": "authentication_failure",
            "source": "auth",
            "username": "gina",
            "source_ip": "3.3.3.3",
        })
    corr = client.post("/api/v1/incidents/correlate?window_minutes=30&min_events=3")
    return corr.json()["incidents"][0]


def test_unauthenticated_proposal_rejected(client: TestClient):
    resp = client.post("/api/v1/responses", json={
        "incident_id": "00000000-0000-0000-0000-000000000000",
        "action_type": "block_test_ip",
        "params": {},
        "risk_class": "HIGH",
    })
    assert resp.status_code == 401


def test_response_action_requires_approval(client: TestClient, admin_headers):
    inc_id = _make_incident(client)
    resp = client.post("/api/v1/responses", json={
        "incident_id": inc_id,
        "action_type": "block_test_ip",
        "params": {"ip": "3.3.3.3"},
        "risk_class": "HIGH",
        "simulation": True,
    }, headers=admin_headers)
    assert resp.status_code == 200
    action_id = resp.json()["action_id"]
    assert resp.json()["status"] == "PENDING_APPROVAL"

    appr = client.post(f"/api/v1/responses/{action_id}/approve", json={
        "decision": "APPROVED",
        "reason": "ok",
    }, headers=admin_headers)
    assert appr.status_code == 200
    assert appr.json()["status"] == "EXECUTED"

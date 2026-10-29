"""Tests for feature engineering."""
from fastapi.testclient import TestClient
from tests.conftest import client

def test_extract_features(client: TestClient):
    # ingest event
    resp = client.post("/api/v1/events", json={
        "timestamp": "2026-09-04T02:13:25Z",
        "event_type": "authentication_failure",
        "source": "test",
        "username": "alice",
        "source_ip": "1.2.3.4",
    })
    event_id = resp.json()["event_id"]
    # extract features
    resp2 = client.post(f"/api/v1/events/{event_id}/features")
    assert resp2.status_code == 200
    data = resp2.json()
    assert "vector" in data
    vec = data["vector"]
    assert vec["event_type"] == "authentication_failure"
    assert "auth_failed_count" in vec
    assert vec["feature_version"] == "v1"

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["simulation_mode"] is True


def test_ready_reports_db_up_and_does_not_crash_without_redis(client):
    # Redis is not running in the test environment; readiness must degrade
    # gracefully instead of erroring (PRD section 52).
    resp = client.get("/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["database"] == "up"
    assert body["redis"] == "down"
    assert body["status"] == "degraded"

"""Authentication, JWT, refresh rotation, and RBAC tests (PRD section 41-42, 46)."""


def test_login_success(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@test.local",
        "password": "AdminPass123!",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0


def test_login_wrong_password(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@test.local",
        "password": "wrong-password",
    })
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "nobody@test.local",
        "password": "whatever123",
    })
    assert resp.status_code == 401


def test_me_with_valid_token(client, admin_headers):
    resp = client.get("/api/v1/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@test.local"
    assert resp.json()["role"] == "ADMIN"


def test_me_without_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)


def test_me_with_invalid_token(client):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.token"})
    assert resp.status_code == 401


def test_refresh_rotation(client):
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@test.local",
        "password": "AdminPass123!",
    }).json()

    # First refresh works and rotates.
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert resp.status_code == 200
    new_pair = resp.json()
    assert new_pair["refresh_token"] != login["refresh_token"]

    # Old refresh token is now revoked (replay rejected).
    replay = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert replay.status_code == 401


def test_access_token_cannot_be_used_as_refresh(client, admin_tokens):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": admin_tokens["access_token"]})
    assert resp.status_code == 401


def test_admin_can_create_user(client, admin_headers):
    resp = client.post("/api/v1/users", headers=admin_headers, json={
        "email": "analyst@test.local",
        "full_name": "Test Analyst",
        "password": "AnalystPass123!",
        "role": "SOC_ANALYST",
    })
    assert resp.status_code == 201
    assert resp.json()["role"] == "SOC_ANALYST"


def test_admin_can_list_users(client, admin_headers):
    resp = client.get("/api/v1/users", headers=admin_headers)
    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert "admin@test.local" in emails


def test_analyst_cannot_manage_users(client):
    # Log in as the analyst created above and try to list users.
    login = client.post("/api/v1/auth/login", json={
        "email": "analyst@test.local",
        "password": "AnalystPass123!",
    })
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resp = client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 403


def test_create_user_rejects_short_password(client, admin_headers):
    resp = client.post("/api/v1/users", headers=admin_headers, json={
        "email": "weak@test.local",
        "password": "short",
        "role": "VIEWER",
    })
    assert resp.status_code == 422


def test_create_user_rejects_bad_role(client, admin_headers):
    resp = client.post("/api/v1/users", headers=admin_headers, json={
        "email": "badrole@test.local",
        "password": "SomePass123!",
        "role": "SUPERUSER",
    })
    assert resp.status_code == 422

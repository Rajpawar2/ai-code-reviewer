from app.core.security import verify_password, get_password_hash, decode_access_token


def test_password_hashing():
    pw = "SecretPass123!"
    hashed = get_password_hash(pw)
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_user_registration(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Password123!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane Doe"


def test_duplicate_registration_fails(client):
    payload = {
        "name": "Jane Doe",
        "email": "duplicate@example.com",
        "password": "Password123!"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    data = res2.json()
    error_msg = data.get("error", {}).get("message") or data.get("detail", "")
    assert "already exists" in error_msg


def test_user_login(client):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "SecurePassword456!"
    }
    client.post("/api/auth/register", json=payload)

    login_res = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "SecurePassword456!"}
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    payload = decode_access_token(data["access_token"])
    assert payload is not None


def test_invalid_login_fails(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrong"}
    )
    assert res.status_code == 401


def test_get_me_authenticated(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "testuser@example.com"


def test_get_me_unauthorized(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401

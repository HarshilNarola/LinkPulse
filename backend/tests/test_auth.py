def test_register_user_success(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert "password_hash" not in data


def test_duplicate_email_fails(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    login_payload = {"email": "alice@example.com", "password": "password123"}
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_token_contains_user_name(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "password123"})
    token = response.json()["access_token"]

    from jose import jwt
    from app.core.config import get_settings

    decoded = jwt.decode(token, get_settings().jwt_secret_key, algorithms=[get_settings().jwt_algorithm])
    assert decoded["name"] == "Alice"


def test_invalid_password_fails(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    login_payload = {"email": "alice@example.com", "password": "wrongpassword"}
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401

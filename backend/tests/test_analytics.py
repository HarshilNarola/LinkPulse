def register_and_login(client, name: str, email: str, password: str):
    client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
    return client.post("/api/auth/login", json={"email": email, "password": password}).json()


def test_click_is_recorded_and_analytics_work(client):
    tokens = register_and_login(client, "Hank", "hank@example.com", "password123")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    created = client.post("/api/urls", json={"original_url": "https://example.com/analytics"}, headers=headers).json()
    client.get(f"/api/urls/redirect/{created['short_code']}")
    response = client.get(f"/api/analytics/{created['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_clicks"] >= 1


def test_normal_user_cannot_access_admin_api(client):
    tokens = register_and_login(client, "Iris", "iris@example.com", "password123")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.get("/api/admin/users", headers=headers)
    assert response.status_code == 403


def test_admin_can_access_admin_api(client):
    admin_payload = {"name": "Admin", "email": "admin@example.com", "password": "password123"}
    client.post("/api/auth/register", json=admin_payload)
    user = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"}).json()

    from app.db.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    admin.role = "ADMIN"
    db.commit()
    db.close()

    headers = {"Authorization": f"Bearer {user['access_token']}"}
    response = client.get("/api/admin/statistics", headers=headers)
    assert response.status_code == 200

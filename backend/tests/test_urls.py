def register_and_login(client, name: str, email: str, password: str):
    client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
    return client.post("/api/auth/login", json={"email": email, "password": password}).json()


def test_authenticated_user_can_create_url(client):
    tokens = register_and_login(client, "Bob", "bob@example.com", "password123")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.post("/api/urls", json={"original_url": "https://example.com"}, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com"
    assert len(data["short_code"]) >= 6


def test_user_can_list_own_urls(client):
    tokens = register_and_login(client, "Cara", "cara@example.com", "password123")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    client.post("/api/urls", json={"original_url": "https://example.com/path"}, headers=headers)
    response = client.get("/api/urls", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_user_cannot_modify_another_users_url(client):
    user1 = register_and_login(client, "Dana", "dana@example.com", "password123")
    user2 = register_and_login(client, "Evan", "evan@example.com", "password123")
    headers1 = {"Authorization": f"Bearer {user1['access_token']}"}
    headers2 = {"Authorization": f"Bearer {user2['access_token']}"}
    created = client.post("/api/urls", json={"original_url": "https://example.com/123"}, headers=headers1).json()
    response = client.put(f"/api/urls/{created['id']}", json={"original_url": "https://evil.com"}, headers=headers2)
    assert response.status_code == 404


def test_short_code_redirect_works(client):
    tokens = register_and_login(client, "Frank", "frank@example.com", "password123")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    created = client.post("/api/urls", json={"original_url": "https://example.com/test"}, headers=headers).json()
    response = client.get(f"/api/urls/redirect/{created['short_code']}")
    assert response.status_code in (200, 307)


def test_expired_url_cannot_redirect(client):
    tokens = register_and_login(client, "Gina", "gina@example.com", "password123")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    created = client.post(
        "/api/urls",
        json={"original_url": "https://example.com/expired", "expires_at": "2000-01-01T00:00:00Z"},
        headers=headers,
    ).json()
    response = client.get(f"/api/urls/redirect/{created['short_code']}")
    assert response.status_code in (410, 403)

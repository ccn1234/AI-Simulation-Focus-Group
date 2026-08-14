def _signup_and_login(client, email, password="password123"):
    client.post("/auth/signup", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_normal_user_cannot_access_admin_dashboard(client):
    token = _signup_and_login(client, "normal@example.com")

    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_dashboard_requires_authentication(client):
    response = client.get("/admin/dashboard")

    assert response.status_code == 401

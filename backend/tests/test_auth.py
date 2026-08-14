def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={"email": "new-user@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new-user@example.com"
    assert response.json()["role"] == "USER"


def test_signup_duplicate_email_is_rejected(client):
    payload = {"email": "duplicate@example.com", "password": "password123"}

    first = client.post("/auth/signup", json=payload)
    second = client.post("/auth/signup", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_returns_access_token(client):
    client.post(
        "/auth/signup",
        json={"email": "login@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_is_rejected(client):
    client.post(
        "/auth/signup",
        json={"email": "wrong-password@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "wrong-password@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code == 401

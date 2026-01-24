def test_register_user(client):
    response = client.post("/register", json={"email": "test@example.com", "password": "securepassword"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_email(client):
    client.post("/register", json={"email": "duplicate@example.com", "password": "123"})
    response = client.post("/register", json={"email": "duplicate@example.com", "password": "456"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    client.post("/register", json={"email": "login@example.com", "password": "correct"})
    response = client.post("/token", data={"username": "login@example.com", "password": "correct"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    client.post("/register", json={"email": "fail@example.com", "password": "correct"})
    response = client.post("/token", data={"username": "fail@example.com", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

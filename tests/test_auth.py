

def test_register_user(client, test_user_data):
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_user_data["name"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data

def test_register_user_with_existing_email(client, test_user_data):
    #First registration should succeed
    response1 = client.post("/auth/register", json=test_user_data)
    assert response1.status_code == 201

    #Second registration with the same email should fail
    response2 = client.post("/auth/register", json=test_user_data)
    assert response2.status_code == 400
    data = response2.json()
    assert data["detail"] == "Email is already registered."


def test_register_user_wrong_repeated_password(client, test_user_data):
    #Modify the test_user_data to have a different repeated password
    test_user_data_with_wrong_repeat = test_user_data.copy()
    test_user_data_with_wrong_repeat["repeat_password"] = "wrongpassword"

    response = client.post("/auth/register", json=test_user_data_with_wrong_repeat)
    assert response.status_code == 422  # Unprocessable Entity 

def test_login_user(client, test_user_data):
    client.post("/auth/register", json=test_user_data)

    response = client.post(
        "/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_credentials(client, test_user_data):
    client.post("/auth/register", json=test_user_data)

    response = client.post(
        "/auth/login",
        data={"username": test_user_data["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password :p."


def test_get_me(client, test_user_data):
    #Register and login the user to get the access token
    client.post("/auth/register", json=test_user_data)
    login_response = client.post(
        "/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]}
    )
    access_token = login_response.json()["access_token"]

    #Use the access token to get the current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_user_data["name"]
    assert data["email"] == test_user_data["email"]


import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register():
    response = client.post("/auth/register", json={
        "email": "new@test.com",
        "username": "newuser",
        "password": "password123",
        "full_name": "New User"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert "id" in response.json()


def test_register_duplicate_username():
    # First registration
    client.post("/auth/register", json={
        "email": "dup@test.com",
        "username": "dupuser",
        "password": "password123"
    })
    
    # Second registration with same username
    response = client.post("/auth/register", json={
        "email": "dup2@test.com",
        "username": "dupuser",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "Username already taken" in response.text


def test_login():
    # Register first
    client.post("/auth/register", json={
        "email": "login@test.com",
        "username": "loginuser",
        "password": "password123"
    })
    
    # Login
    response = client.post("/auth/login", data={
        "username": "loginuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid():
    response = client.post("/auth/login", data={
        "username": "wronguser",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert "Invalid username or password" in response.text
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_token(client):
    # Register user
    client.post("/auth/register", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    
    # Login
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    return response.json()["access_token"]
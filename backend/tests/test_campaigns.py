import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_campaign(auth_token):
    response = client.post("/campaigns", 
        json={
            "name": "Test Campaign",
            "budget": 10000,
            "start_date": "2024-01-01",
            "currency": "USD",
            "status": "Draft"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Campaign"
    assert response.json()["budget"] == 10000


def test_get_campaigns(auth_token):
    # Create a campaign first
    client.post("/campaigns", 
        json={
            "name": "List Test",
            "budget": 5000,
            "start_date": "2024-01-01",
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    response = client.get("/campaigns", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_campaign_not_found(auth_token):
    response = client.get("/campaigns/99999", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_update_campaign(auth_token):
    # Create
    create = client.post("/campaigns", 
        json={
            "name": "Update Test",
            "budget": 10000,
            "start_date": "2024-01-01",
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    campaign_id = create.json()["id"]
    
    # Update
    response = client.put(f"/campaigns/{campaign_id}",
        json={
            "name": "Updated Name",
            "budget": 20000,
            "start_date": "2024-01-01",
            "currency": "USD",
            "status": "Active"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["budget"] == 20000
    assert response.json()["status"] == "Active"


def test_delete_campaign(auth_token):
    # Create
    create = client.post("/campaigns", 
        json={
            "name": "Delete Test",
            "budget": 10000,
            "start_date": "2024-01-01",
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    campaign_id = create.json()["id"]
    
    # Delete
    response = client.delete(f"/campaigns/{campaign_id}", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204
    
    # Verify deleted
    get = client.get(f"/campaigns/{campaign_id}", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get.status_code == 404


def test_duplicate_campaign(auth_token):
    # Create
    create = client.post("/campaigns", 
        json={
            "name": "Duplicate Test",
            "budget": 10000,
            "start_date": "2024-01-01",
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    campaign_id = create.json()["id"]
    
    # Duplicate
    response = client.post(f"/campaigns/{campaign_id}/duplicate",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    assert "Copy" in response.json()["name"]
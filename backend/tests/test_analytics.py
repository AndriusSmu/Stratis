import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analytics_stats(auth_token):
    # Create multiple campaigns
    campaigns = [
        {"name": "Analytics 1", "budget": 10000, "start_date": "2024-01-01", "currency": "USD", "status": "Active"},
        {"name": "Analytics 2", "budget": 20000, "start_date": "2024-01-01", "currency": "USD", "status": "Draft"},
        {"name": "Analytics 3", "budget": 15000, "start_date": "2024-01-01", "currency": "USD", "status": "Active"},
    ]
    
    for c in campaigns:
        client.post("/campaigns", json=c, headers={"Authorization": f"Bearer {auth_token}"})
    
    response = client.get("/analytics/stats", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["campaign_count"] >= 3
    assert data["total_budget_usd"] >= 45000
    assert data["status_counts"]["Active"] >= 2
    assert data["status_counts"]["Draft"] >= 1
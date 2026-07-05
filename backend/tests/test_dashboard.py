import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dashboard_stats(auth_token):
    response = client.get("/dashboard/stats", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "active_budget_usd" in data
    assert "total_budget_usd" in data
    assert "total_spent_usd" in data
    assert "counts_by_status" in data
    assert "expired_count" in data
    assert "total_campaigns" in data
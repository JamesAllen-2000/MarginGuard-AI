from fastapi.testclient import TestClient
from main import app
from models.schemas import SKUBase

client = TestClient(app)

sample_sku_data = {
    "id": "SKU123",
    "name": "High Risk Item",
    "asin": "B01",
    "currentPrice": 49.99,
    "cogs": 10.0,
    "fbaFees": 15.0,
    "referralFees": 7.5,
    "adSpend30d": 500.0,
    "revenue30d": 1000.0,
    "unitsSold30d": 20,
    "returns30d": 5,
    "currentMargin": -5.0,
    "marginTrend": "down",
    "salesVelocity": 0.6,
    "acos": 50.0,
    "lastUpdated": "2023-01-01T00:00:00Z"
}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_risk_score():
    response = client.post("/api/v1/risk-score", json=sample_sku_data)
    assert response.status_code == 200
    data = response.json()
    assert data["skuId"] == "SKU123"
    assert data["riskLevel"] == "high" # It has negative margin, high ACOS, so it should be high risk
    assert len(data["factors"]) == 4

def test_explanation():
    response = client.post("/api/v1/explanation", json=sample_sku_data)
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert data["skuId"] == "SKU123"

def test_simulate():
    req = {
        "skuId": "SKU123",
        "newPrice": 55.0,
        "skuData": sample_sku_data
    }
    response = client.post("/api/v1/simulate", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["before"]["price"] == 49.99
    assert data["after"]["price"] == 55.0

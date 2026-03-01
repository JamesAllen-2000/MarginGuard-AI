from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_get_raw_data_template():
    response = client.get("/api/v1/raw-data/template")
    assert response.status_code == 200
    data = response.json()
    assert "sample_payload" in data
    assert "message" in data

@patch("services.supabase_client.SupabaseClient.save_raw_json")
@patch("services.bedrock_client.BedrockClient.generate_explanation")
def test_analyze_raw_data(mock_generate_explanation, mock_save_raw_json):
    # Setup mocks
    mock_generate_explanation.return_value = "Mocked explanation"
    mock_save_raw_json.return_value = True

    # Partial raw data payload
    raw_payload = {
        "name": "Test Shirt",
        "currentPrice": 20.0,
        "cogs": 5.0,
        "fbaFees": 2.0,
        "referralFees": 3.0,
        "revenue30d": 1000.0,
        "adSpend30d": 150.0,
        "custom_field": "Should be ignored by risk engine but saved"
    }

    response = client.post("/api/v1/raw-data/analyze", json=raw_payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Asserting response structure
    assert data["explanation"] == "Mocked explanation"
    assert "skuId" in data
    assert "riskFactors" in data
    assert "score" in data
    
    # Assert Supabase was called
    mock_save_raw_json.assert_called_once()
    assert mock_save_raw_json.call_args[1]["payload"]["custom_field"] == "Should be ignored by risk engine but saved"

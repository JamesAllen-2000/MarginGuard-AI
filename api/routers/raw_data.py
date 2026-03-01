from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
from models.schemas import RawSKUData, AIExplanationResponse
from core.risk_engine import calculate_risk
from services.bedrock_client import BedrockClient
from services.supabase_client import SupabaseClient

router = APIRouter(prefix="/api/v1/raw-data", tags=["Raw Data Ingestion"])

def get_bedrock():
    return BedrockClient()

def get_supabase():
    return SupabaseClient()

@router.get("/template")
async def get_raw_data_template():
    """
    Returns a sample JSON payload showing the flexible structure we accept.
    """
    return {
        "message": "Send your unstructured or partially structured JSON to POST /api/v1/raw-data/analyze",
        "sample_payload": {
            "name": "Summer T-Shirt",
            "currentPrice": 25.99,
            "cogs": 8.50,
            "fbaFees": 4.00,
            "referralFees": 3.90,
            "revenue30d": 1200.0,
            "adSpend30d": 150.0,
            "extra_frontend_data": "This will be saved to Supabase but ignored by the AI"
        }
    }

@router.post("/analyze", response_model=AIExplanationResponse)
async def analyze_raw_data(
    request: Request,
    bedrock: BedrockClient = Depends(get_bedrock),
    supabase: SupabaseClient = Depends(get_supabase)
):
    """
    Accepts raw JSON, structures it, saves to Supabase, and runs AI analysis.
    """
    try:
        # Try to parse the raw body as JSON
        raw_payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # 1. Structure the raw data into our working model
    try:
        raw_data_model = RawSKUData(**raw_payload)
        # Keep the exact raw payload just in case there were fields not defined in RawSKUData
        raw_data_model.raw_payload = raw_payload 
        sku_base = raw_data_model.to_sku_base()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Data mapping error: {str(e)}")

    # 2. Run Risk Logic
    score, factors = calculate_risk(sku_base)

    # 3. Save to Supabase (Database)
    supabase.save_raw_json(
        sku_id=sku_base.id, 
        payload=raw_payload, 
        processed_data=sku_base.model_dump()
    )

    # 4. Generate AI Explanation
    explanation = bedrock.generate_explanation(
        sku_name=sku_base.name,
        margin=sku_base.currentMargin,
        score=score,
        factors=factors
    )

    return AIExplanationResponse(
        skuId=sku_base.id,
        explanation=explanation,
        riskFactors=factors,
        score=score
    )

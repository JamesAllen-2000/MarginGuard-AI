from fastapi import APIRouter, HTTPException, Depends
from models.schemas import SKUBase, SKURiskResponse, AIExplanationResponse, SimulateRequest, SimulationResult
from core.risk_engine import calculate_risk, get_risk_level
from core.simulator import simulate_price_change
from services.ai.factory import AIClientFactory
from services.ai.base_client import BaseAIClient

router = APIRouter(prefix="/api/v1", tags=["Intelligence"])

def get_ai_service() -> BaseAIClient:
    return AIClientFactory.get_ai_client()

@router.post("/risk-score", response_model=SKURiskResponse)
async def get_risk_score(sku: SKUBase):
    """Calculate the Margin Risk Score for a given SKU."""
    score, factors = calculate_risk(sku)
    level = get_risk_level(score)
    
    return SKURiskResponse(
        skuId=sku.id,
        riskScore=score,
        riskLevel=level,
        factors=factors
    )

@router.post("/explanation", response_model=AIExplanationResponse)
async def get_explanation(sku: SKUBase, ai_service: BaseAIClient = Depends(get_ai_service)):
    """Generate an AI explanation of risk factors for a given SKU."""
    score, factors = calculate_risk(sku)
    
    explanation = ai_service.generate_explanation(
        sku_name=sku.name,
        margin=sku.currentMargin,
        score=score,
        factors=factors
    )
    
    return AIExplanationResponse(
        skuId=sku.id,
        explanation=explanation,
        riskFactors=factors,
        score=score
    )

@router.post("/simulate", response_model=SimulationResult)
async def simulate_scenario(request: SimulateRequest):
    """Simulate the financial and risk impact of a price change."""
    if request.newPrice < request.skuData.currentPrice * 0.5 or request.newPrice > request.skuData.currentPrice * 2.0:
        raise HTTPException(status_code=400, detail="Price adjustment must be between -50% and +100%")
        
    result = simulate_price_change(request.skuData, request.newPrice)
    return result

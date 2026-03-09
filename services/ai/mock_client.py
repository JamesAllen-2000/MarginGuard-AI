import logging
from typing import List
from models.schemas import RiskFactor
from services.ai.base_client import BaseAIClient

logger = logging.getLogger(__name__)

class MockClient(BaseAIClient):
    """
    A lightweight Mock AI Client for local testing or situations where no external API keys are configured.
    Generates deterministic string responses mimicking AI output.
    """
    
    def __init__(self):
        logger.info("Mock AI Client initialized.")
        
    def generate_explanation(self, sku_name: str, margin: float, score: float, factors: List[RiskFactor]) -> str:
        top_factor = factors[0].name if factors else "Unidentified margin erosion"
        impact_val = factors[0].impact if factors else "significant"
        
        explanation = (
            f"[MOCK AI Generated]: Analysis for {sku_name} indicates a critical risk score of {score:.1f}/100. "
            f"The primary driver is '{top_factor}' carrying an impact weight of {impact_val}. "
            f"Current margin has dropped to {margin:.1f}%. Immediate tactical price adjustment or cost investigation is advised."
        )
        return explanation

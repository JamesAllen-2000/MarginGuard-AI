import logging
import json
from typing import List
from models.schemas import RiskFactor
from services.ai.base_client import BaseAIClient
from core.config import settings

logger = logging.getLogger(__name__)

# To use this client, the user must install the 'openai' python package.
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class OpenAIClient(BaseAIClient):
    """
    OpenAI integration for MarginGuard AI explanations.
    """
    
    def __init__(self):
        if not HAS_OPENAI:
            logger.warning("OpenAI package not found. Generating explanations will fail unless it is installed (pip install openai).")
            self.client = None
        elif not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured. Generating explanations will fail.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized successfully.")
            
    def generate_explanation(self, sku_name: str, margin: float, score: float, factors: List[RiskFactor]) -> str:
        if not self.client:
           return f"System Warning: OpenAI Client unavailable for {sku_name}. Ensure API key and module are installed."
           
        factors_text_list = [f"{i+1}. {f.name}: {f.dataPoint}" for i, f in enumerate(factors[:3])]
        factors_text = "\n".join(factors_text_list)
        
        system_prompt = "You are an AI financial analyst helping Amazon FBA sellers understand profit risks. Keep it to 2-3 actionable sentences."
        user_prompt = f"""
SKU: {sku_name}
Current Margin: {margin}%
Risk Score: {score}/100

Top Risk Factors:
{factors_text}

Provide a concise explanation for the risk score.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("OpenAI Error: %s", e, exc_info=True)
            return f"Error contacting OpenAI: Failed to generate insights for {sku_name}."

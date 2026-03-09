from abc import ABC, abstractmethod
from typing import List
from models.schemas import RiskFactor

class BaseAIClient(ABC):
    """
    Abstract Base Class for AI Clients in MarginGuard AI.
    Any new AI provider (OpenAI, Bedrock, Gemini, etc.) must implement these methods.
    """

    @abstractmethod
    def generate_explanation(self, sku_name: str, margin: float, score: float, factors: List[RiskFactor]) -> str:
        """
        Generate a natural language explanation for why a SKU is at risk.

        Args:
            sku_name (str): Name of the product (e.g., "Premium Yoga Mat")
            margin (float): The current profit margin percentage (e.g., 35.5)
            score (float): The calculated risk score from 0-100 (e.g., 85)
            factors (List[RiskFactor]): A list of the top contributing risk factors.

        Returns:
            str: A natural language explanation answering why this SKU is at risk and what might happen next.
        """
        pass

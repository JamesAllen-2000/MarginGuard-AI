import logging
from core.config import settings
from services.ai.base_client import BaseAIClient
from services.ai.bedrock_client import BedrockClient
from services.ai.openai_client import OpenAIClient
from services.ai.mock_client import MockClient

logger = logging.getLogger(__name__)

class AIClientFactory:
    """
    Factory class to instantiate and return the configured AI Client provider.
    Based on settings.active_ai_provider ("bedrock", "openai", "mock").
    """
    
    @staticmethod
    def get_ai_client() -> BaseAIClient:
        provider = settings.active_ai_provider.lower().strip()
        
        if provider == "openai":
            logger.info("AI Factory routing to OpenAI Client")
            return OpenAIClient()
            
        elif provider == "mock":
            logger.info("AI Factory routing to Mock Client")
            return MockClient()
            
        elif provider == "bedrock":
            logger.info("AI Factory routing to AWS Bedrock Client")
            return BedrockClient()
            
        else:
            logger.warning(f"Unknown AI provider '{provider}', falling back to MockClient")
            return MockClient()

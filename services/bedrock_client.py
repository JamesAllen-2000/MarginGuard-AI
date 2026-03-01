import boto3
import json
import logging
from typing import List
from botocore.exceptions import ClientError
from services.prompts import BEDROCK_EXPLANATION_PROMPT
from models.schemas import RiskFactor
from core.config import settings

logger = logging.getLogger(__name__)

class BedrockClient:
    def __init__(self):
        try:
            # Explicitly load from settings if provided (useful for local testing)
            # In a production ECS/Lambda environment, boto3 will automatically pick up IAM roles 
            # if we leave keys as None.
            session_kwargs = {
                "region_name": settings.aws_region
            }
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
                session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

            self.client = boto3.client(service_name='bedrock-runtime', **session_kwargs)
            logger.info("Bedrock client initialized successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize Bedrock client, using mock. Error: {e}")
            self.client = None

    def generate_explanation(self, sku_name: str, margin: float, score: float, factors: List[RiskFactor]) -> str:
        factors_text_list = [f"{i+1}. {f.name}: {f.dataPoint}" for i, f in enumerate(factors[:3])]
        factors_text = "\n".join(factors_text_list)
        
        prompt = BEDROCK_EXPLANATION_PROMPT.format(
            sku_name=sku_name,
            margin=margin,
            risk_score=score,
            factors_text=factors_text
        )

        if not self.client:
            # Return mock response
            logger.info("Using mock Bedrock response for SKU %s", sku_name)
            top_factor = factors[0].name.lower() if factors else "unknown risks"
            return f"Mock Warning: {sku_name} has a risk score of {score:.1f}/100 mainly due to {top_factor}. Addressing {top_factor} could help stabilize profit margins."

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 150,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })

            response = self.client.invoke_model(
                body=body,
                modelId=settings.bedrock_model_id,
                accept="application/json",
                contentType="application/json"
            )

            response_body = json.loads(response.get('body').read())
            explanation = response_body.get("content", [{}])[0].get("text", "")
            return explanation.strip()

        except ClientError as e:
            logger.error("AWS ClientError calling Bedrock: %s", e)
            top_factor = factors[0].name.lower() if factors else "unknown risks"
            return f"Service Unavailable. Mock Warning (Fallback): {sku_name} is at risk mainly due to {top_factor}."
        except Exception as e:
            logger.error("Unexpected error calling Bedrock: %s", e, exc_info=True)
            top_factor = factors[0].name.lower() if factors else "unknown risks"
            return f"Failed to generate insights. Mock Warning (Fallback): {sku_name} is at risk mainly due to {top_factor}."

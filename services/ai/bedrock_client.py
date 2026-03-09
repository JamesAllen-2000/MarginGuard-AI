import boto3
import json
import logging
import os
from typing import List
from botocore.exceptions import ClientError
from services.prompts import BEDROCK_EXPLANATION_PROMPT
from models.schemas import RiskFactor
from core.config import settings
from services.ai.base_client import BaseAIClient

logger = logging.getLogger(__name__)

class BedrockClient(BaseAIClient):
    def __init__(self):
        try:
            session_kwargs = {
                "region_name": settings.aws_region
            }
            
            # Use Bearer Token if available
            if settings.aws_bearer_token_bedrock:
                # Export to environment for native boto3 bearer token support
                os.environ["AWS_BEARER_TOKEN_BEDROCK"] = settings.aws_bearer_token_bedrock
                
                # Provide dummy SigV4 creds to avoid NoCredentialsError;
                # the event hook below will override with the Bearer Token.
                if not (settings.aws_access_key_id and settings.aws_secret_access_key):
                    session_kwargs["aws_access_key_id"] = "dummy"
                    session_kwargs["aws_secret_access_key"] = "dummy"
                
                self.client = boto3.client(service_name='bedrock-runtime', **session_kwargs)
                
                # Inject the Bearer Token into every outgoing request
                def add_bearer_token(request, **kwargs):
                    request.headers['Authorization'] = f'Bearer {settings.aws_bearer_token_bedrock}'
                
                # Override any SigV4 signing with our bearer token
                self.client.meta.events.register('before-sign.bedrock-runtime.*', add_bearer_token)
                logger.info("Bedrock client initialized with Bearer Token handler.")
                
            else:
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
            logger.info("Using mock Bedrock response for SKU %s", sku_name)
            top_factor = factors[0].name.lower() if factors else "unknown risks"
            return f"Mock Warning: {sku_name} has a risk score of {score:.1f}/100 mainly due to {top_factor}. Addressing {top_factor} could help stabilize profit margins."

        try:
            # DeepSeek on Bedrock uses OpenAI-compatible messages format.
            # Note: Do NOT include 'model' in the body — it's passed via modelId parameter.
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7
            })

            response = self.client.invoke_model(
                body=body,
                modelId=settings.bedrock_model_id,
                accept="application/json",
                contentType="application/json"
            )

            response_body = json.loads(response.get('body').read())
            logger.debug("Bedrock raw response: %s", response_body)

            # DeepSeek / OpenAI-compatible format: choices[0].message.content
            choices = response_body.get("choices", [])
            if choices:
                explanation = choices[0].get("message", {}).get("content", "")
            else:
                # Fallback: try Anthropic format
                explanation = response_body.get("content", [{}])[0].get("text", "")
            return explanation.strip()

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            logger.error("AWS ClientError calling Bedrock [%s]: %s", error_code, error_msg)
            top_factor = factors[0].name.lower() if factors else "unknown risks"
            return f"Bedrock Error ({error_code}): {sku_name} is at risk mainly due to {top_factor}. Check API credentials/model ID."
        except Exception as e:
            logger.error("Unexpected error calling Bedrock: %s", e, exc_info=True)
            top_factor = factors[0].name.lower() if factors else "unknown risks"
            return f"Failed to generate insights. Mock Warning (Fallback): {sku_name} is at risk mainly due to {top_factor}."

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # API configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "MarginGuard AI Microservice"
    debug: bool = False
    
    # CORS
    backend_cors_origins: List[str] = ["*"] # Set to your frontend URL in prod e.g., ["https://marginguard.com"]
    
    # AWS & Bedrock
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # AWS Credentials (optional for local/serverless env with assumed roles)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()

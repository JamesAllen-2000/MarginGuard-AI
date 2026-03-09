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
    bedrock_model_id: str = "deepseek.deepseek-v3-0324"  # Override with BEDROCK_MODEL_ID in .env if needed
    aws_bearer_token_bedrock: str | None = None
    
    # Interchangeable AI
    active_ai_provider: str = "bedrock" # options: "bedrock", "openai", "mock"
    openai_api_key: str | None = None
    
    # Supabase configuration
    supabase_url: str = ""
    supabase_key: str = ""
    
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

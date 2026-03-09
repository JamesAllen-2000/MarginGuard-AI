import json
import os
import boto3
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from models.schemas import SKUBase, SKURiskResponse
from core.risk_engine import calculate_risk, get_risk_level
from core.config import settings

router = APIRouter(prefix="/api/v1/skus", tags=["SKUs"])

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "skus.json")

def load_skus() -> List[SKUBase]:
    bucket_name = getattr(settings, "s3_bucket_name", None)
    file_key = getattr(settings, "data_file_key", "skus.json")
    
    data = None
    
    # Try loading from S3 first (Requirement 2.5, 8.4)
    if bucket_name:
        try:
            s3_client = boto3.client('s3', region_name=settings.aws_region)
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            content = response['Body'].read().decode('utf-8')
            parsed = json.loads(content)
            # Handle potential nested structure like {"skus": [...]} mentioned in design.md
            if isinstance(parsed, dict) and "skus" in parsed:
                data = parsed["skus"]
            elif isinstance(parsed, list):
                data = parsed
        except Exception as e:
            print(f"Warning: Failed to load SKUs from S3 bucket {bucket_name}: {e}. Falling back to local file.")
            
    # Fallback to local file
    if data is None:
        try:
            with open(DATA_PATH, "r") as f:
                parsed = json.load(f)
                if isinstance(parsed, dict) and "skus" in parsed:
                    data = parsed["skus"]
                elif isinstance(parsed, list):
                    data = parsed
        except Exception as e:
            print(f"Error loading local SKUs: {e}")
            return []
            
    if data:
        return [SKUBase(**item) for item in data]
    return []

@router.get("/", response_model=List[SKUBase])
async def get_skus(
    riskLevel: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    search: Optional[str] = None
):
    """
    Retrieve all SKUs with optional filtering.
    """
    skus = load_skus()
    
    filtered_skus = []
    for sku in skus:
        # Calculate risk for filtering
        score, _ = calculate_risk(sku)
        level = get_risk_level(score)
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            if search_lower not in sku.name.lower() and search_lower not in sku.id.lower() and search_lower not in sku.asin.lower():
                continue
        
        # Apply risk level filter
        if riskLevel and level != riskLevel:
            continue
            
        filtered_skus.append(sku)
        
    return filtered_skus

@router.get("/{sku_id}", response_model=SKUBase)
async def get_sku(sku_id: str):
    """
    Retrieve a single SKU by ID.
    """
    skus = load_skus()
    for sku in skus:
        if sku.id == sku_id:
            return sku
    raise HTTPException(status_code=404, detail=f"SKU {sku_id} not found")

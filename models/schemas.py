from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, List, Optional, Dict, Any
import datetime

class SKUBase(BaseModel):
    id: str
    name: str
    asin: str
    currentPrice: float
    cogs: float
    fbaFees: float
    referralFees: float
    adSpend30d: float
    revenue30d: float
    unitsSold30d: int
    returns30d: int
    currentMargin: float
    marginTrend: Literal['up', 'down', 'stable']
    salesVelocity: float
    acos: float
    lastUpdated: str

class RiskFactor(BaseModel):
    name: str
    impact: float
    dataPoint: str
    severity: Literal['low', 'medium', 'high']

class SKURiskResponse(BaseModel):
    skuId: str
    riskScore: float
    riskLevel: Literal['low', 'medium', 'high']
    factors: List[RiskFactor]

class AIExplanationResponse(BaseModel):
    skuId: str
    explanation: str
    riskFactors: List[RiskFactor]
    score: float

class SimulateRequest(BaseModel):
    skuId: str
    newPrice: float
    skuData: SKUBase

class MetricsBefore(BaseModel):
    price: float
    margin: float
    riskScore: float
    projectedRevenue30d: float

class MetricsAfter(BaseModel):
    price: float
    margin: float
    riskScore: float
    projectedRevenue30d: float
    estimatedVolumeChange: float

class SimulationResult(BaseModel):
    before: MetricsBefore
    after: MetricsAfter

class RawSKUData(BaseModel):
    """
    Accepts raw unstructured JSON from the frontend.
    Allows for missing fields and provides defaults or calculated values
    so it can be correctly processed by the risk engine.
    """
    id: Optional[str] = Field(default_factory=lambda: f"SKU-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    name: Optional[str] = "Unknown Item"
    asin: Optional[str] = "UNKNOWN"
    currentPrice: Optional[float] = 0.0
    cogs: Optional[float] = 0.0
    fbaFees: Optional[float] = 0.0
    referralFees: Optional[float] = 0.0
    adSpend30d: Optional[float] = 0.0
    revenue30d: Optional[float] = 0.0
    unitsSold30d: Optional[int] = 0
    returns30d: Optional[int] = 0
    currentMargin: Optional[float] = None
    marginTrend: Optional[str] = "stable"
    salesVelocity: Optional[float] = 0.0
    acos: Optional[float] = None
    lastUpdated: Optional[str] = None
    
    # Catch-all for extra raw data we want to keep
    raw_payload: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")

    def to_sku_base(self) -> SKUBase:
        """Converts this raw data into the strict SKUBase format."""
        
        # Calculate currentMargin if not provided
        margin = self.currentMargin
        if margin is None:
            if self.currentPrice > 0:
                total_costs = self.cogs + self.fbaFees + self.referralFees
                margin = ((self.currentPrice - total_costs) / self.currentPrice) * 100.0
            else:
                margin = 0.0
                
        # Calculate ACOS if not provided
        acos_val = self.acos
        if acos_val is None:
            if self.revenue30d > 0:
                acos_val = (self.adSpend30d / self.revenue30d) * 100.0
            else:
                acos_val = 0.0
                
        # Map margin trend
        trend = "stable"
        if self.marginTrend and self.marginTrend.lower() in ("up", "down", "stable"):
            trend = self.marginTrend.lower()
            
        update_time = self.lastUpdated or datetime.datetime.utcnow().isoformat()
        
        return SKUBase(
            id=self.id,
            name=self.name,
            asin=self.asin,
            currentPrice=self.currentPrice,
            cogs=self.cogs,
            fbaFees=self.fbaFees,
            referralFees=self.referralFees,
            adSpend30d=self.adSpend30d,
            revenue30d=self.revenue30d,
            unitsSold30d=self.unitsSold30d,
            returns30d=self.returns30d,
            currentMargin=margin,
            marginTrend=trend,
            salesVelocity=self.salesVelocity,
            acos=acos_val,
            lastUpdated=update_time
        )

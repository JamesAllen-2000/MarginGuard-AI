from pydantic import BaseModel, Field
from typing import Literal, List, Optional

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

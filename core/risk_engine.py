from typing import Tuple, List
from models.schemas import SKUBase, RiskFactor

def _calculate_margin_trend_score(sku: SKUBase) -> Tuple[float, RiskFactor]:
    if sku.marginTrend == 'up':
        score = 0.0
        severity = 'low'
        dp = "Margin is improving"
    elif sku.marginTrend == 'stable':
        score = 30.0
        severity = 'low'
        dp = "Margin is stable"
    else:
        score = 100.0
        severity = 'high'
        dp = "Margin has been declining"
    
    factor = RiskFactor(
        name="Margin Trend",
        impact=score * 0.4,
        dataPoint=dp,
        severity=severity
    )
    return score, factor

def _calculate_ad_efficiency_score(sku: SKUBase) -> Tuple[float, RiskFactor]:
    # ACOS > 50% => 100, ACOS < 15% => 0
    if sku.acos > 50:
        score = 100.0
        severity = 'high'
    elif sku.acos < 15:
        score = 0.0
        severity = 'low'
    else:
        score = (sku.acos - 15) / (50 - 15) * 100.0
        severity = 'medium' if score < 70 else 'high'
        
    factor = RiskFactor(
        name="Ad Efficiency",
        impact=score * 0.3,
        dataPoint=f"ACOS is {sku.acos}%",
        severity=severity
    )
    return score, factor

def _calculate_fee_impact_score(sku: SKUBase) -> Tuple[float, RiskFactor]:
    # fee % > 45% => 100, < 25% => 0
    fee_pct = ((sku.fbaFees + sku.referralFees) / sku.currentPrice) * 100 if sku.currentPrice > 0 else 100
    
    if fee_pct > 45:
        score = 100.0
        severity = 'high'
    elif fee_pct < 25:
        score = 0.0
        severity = 'low'
    else:
        score = (fee_pct - 25) / (45 - 25) * 100.0
        severity = 'medium' if score < 70 else 'high'

    factor = RiskFactor(
        name="Fee Impact",
        impact=score * 0.2,
        dataPoint=f"Fees consume {fee_pct:.1f}% of revenue",
        severity=severity
    )
    return score, factor

def _calculate_return_rate_score(sku: SKUBase) -> Tuple[float, RiskFactor]:
    # Return rate > 10% => 100, < 2% => 0
    return_rate = (sku.returns30d / sku.unitsSold30d) * 100 if sku.unitsSold30d > 0 else 0
    
    if return_rate > 10:
        score = 100.0
        severity = 'high'
    elif return_rate < 2:
        score = 0.0
        severity = 'low'
    else:
        score = (return_rate - 2) / (10 - 2) * 100.0
        severity = 'medium' if score < 70 else 'high'

    factor = RiskFactor(
        name="Return Rate",
        impact=score * 0.1,
        dataPoint=f"Return rate is {return_rate:.1f}%",
        severity=severity
    )
    return score, factor


def calculate_risk(sku: SKUBase) -> Tuple[float, List[RiskFactor]]:
    """
    Calculate risk score between 0 and 100.
    """
    margin_score, margin_factor = _calculate_margin_trend_score(sku)
    ad_score, ad_factor = _calculate_ad_efficiency_score(sku)
    fee_score, fee_factor = _calculate_fee_impact_score(sku)
    ret_score, ret_factor = _calculate_return_rate_score(sku)
    
    final_score = (
        (margin_score * 0.4) +
        (ad_score * 0.3) +
        (fee_score * 0.2) +
        (ret_score * 0.1)
    )
    
    # Cap between 0 and 100
    final_score = max(0.0, min(100.0, final_score))
    
    factors = sorted([margin_factor, ad_factor, fee_factor, ret_factor], key=lambda x: x.impact, reverse=True)
    return final_score, factors

def get_risk_level(score: float) -> str:
    if score <= 39:
        return 'low'
    elif score <= 69:
        return 'medium'
    return 'high'

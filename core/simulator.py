from models.schemas import SKUBase, SimulationResult, MetricsBefore, MetricsAfter

def simulate_price_change(sku: SKUBase, new_price: float) -> SimulationResult:
    # 1. Calculate price change %
    old_price = sku.currentPrice
    
    if old_price <= 0:
        price_change_pct = 0
    else:
        price_change_pct = ((new_price - old_price) / old_price) * 100
        
    # 2. Estimated volume change
    # Elasticity of -0.8
    # Decrease => volume increase, Increase => volume decrease
    est_vol_change_pct = -(price_change_pct) * 0.8
    
    # 3. Calculate new volume (last 30 days)
    new_vol = sku.unitsSold30d * (1 + est_vol_change_pct / 100.0)
    new_vol = max(0, new_vol)
    
    # 4. New Revenue
    new_rev = new_vol * new_price
    
    # 5. New Margin
    cogs = sku.cogs
    fees = sku.fbaFees + sku.referralFees
    if new_price > 0:
        new_margin = ((new_price - cogs - fees) / new_price) * 100
    else:
        new_margin = -100.0 # Just a fallback for zero price
        
    # We should calculate the new risk score
    # We create a pseudo SKU object for this
    sku_simulated = sku.model_copy()
    sku_simulated.currentPrice = new_price
    sku_simulated.currentMargin = new_margin
    sku_simulated.unitsSold30d = int(new_vol)
    sku_simulated.revenue30d = new_rev
    
    from core.risk_engine import calculate_risk
    
    old_score, _ = calculate_risk(sku)
    new_score, _ = calculate_risk(sku_simulated)
    
    res = SimulationResult(
        before=MetricsBefore(
            price=old_price,
            margin=sku.currentMargin,
            riskScore=old_score,
            projectedRevenue30d=sku.revenue30d
        ),
        after=MetricsAfter(
            price=new_price,
            margin=new_margin,
            riskScore=new_score,
            projectedRevenue30d=new_rev,
            estimatedVolumeChange=est_vol_change_pct
        )
    )
    
    return res

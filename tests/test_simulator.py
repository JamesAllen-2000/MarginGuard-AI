import pytest
from hypothesis import given, strategies as st
from models.schemas import SKUBase
from core.simulator import simulate_price_change

sku_sim_strategy = st.builds(
    SKUBase,
    id=st.text(min_size=1),
    name=st.text(min_size=1),
    asin=st.text(min_size=1),
    currentPrice=st.floats(min_value=10.0, max_value=100.0),
    cogs=st.floats(min_value=1.0, max_value=5.0),
    fbaFees=st.floats(min_value=1.0, max_value=5.0),
    referralFees=st.floats(min_value=1.0, max_value=5.0),
    adSpend30d=st.floats(min_value=10.0, max_value=100.0),
    revenue30d=st.floats(min_value=100.0, max_value=1000.0),
    unitsSold30d=st.integers(min_value=10, max_value=100),
    returns30d=st.integers(min_value=0, max_value=5),
    currentMargin=st.floats(min_value=10.0, max_value=50.0),
    marginTrend=st.sampled_from(['up', 'down', 'stable']),
    salesVelocity=st.floats(min_value=1.0, max_value=5.0),
    acos=st.floats(min_value=5.0, max_value=25.0),
    lastUpdated=st.text(min_size=1)
)

# Feature: marginguard-ai-mvp, Property 17: Price Elasticity Simulation
@given(sku_sim_strategy, st.floats(min_value=5.0, max_value=200.0))
def test_price_elasticity_simulation_bounds(sku: SKUBase, new_price: float):
    # As long as it operates, it should return a valid SimulationResult
    res = simulate_price_change(sku, new_price)
    assert res.before.price == sku.currentPrice
    assert res.after.price == new_price
    
    # Check volume change elasticity formula
    expected_pct_change = -(((new_price - sku.currentPrice) / sku.currentPrice) * 100) * 0.8
    assert abs(res.after.estimatedVolumeChange - expected_pct_change) < 0.01

def test_simulation_specific_scenario():
    """Specific unit test for elasticity formula and margin calculation"""
    sku = SKUBase(
        id="SIM1", name="Sim Item", asin="B000",
        currentPrice=100.0, cogs=20.0,
        fbaFees=20.0, referralFees=10.0, # Total cost = 50. Margin = (100-50)/100 = 50%
        adSpend30d=100.0, revenue30d=10000.0,
        unitsSold30d=100, returns30d=5,
        currentMargin=50.0, marginTrend='stable',
        salesVelocity=3.3, acos=10.0, lastUpdated="2023-01-01"
    )
    
    # Increase price by 10% to 110.0
    # Price change = +10%
    # Estimated volume change = 10% * -0.8 = -8%
    # New Volume = 100 * (1 - 0.08) = 92
    
    res = simulate_price_change(sku, 110.0)
    assert res.after.estimatedVolumeChange == -8.0
    
    # New total cost = cogs + fees = 20 + 30 = 50
    # New Margin = (110 - 50) / 110 = 60 / 110 = 54.5454%
    assert abs(res.after.margin - 54.545) < 0.01
    
    # New Revenue = 92 volume * 110 price = 10120
    assert res.after.projectedRevenue30d == 10120.0

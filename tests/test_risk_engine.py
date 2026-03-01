import pytest
from hypothesis import given, strategies as st
from models.schemas import SKUBase
from core.risk_engine import calculate_risk, get_risk_level

sku_strategy = st.builds(
    SKUBase,
    id=st.text(min_size=1),
    name=st.text(min_size=1),
    asin=st.text(min_size=1),
    currentPrice=st.floats(min_value=0.1, max_value=1000.0),
    cogs=st.floats(min_value=0.0, max_value=1000.0),
    fbaFees=st.floats(min_value=0.0, max_value=500.0),
    referralFees=st.floats(min_value=0.0, max_value=500.0),
    adSpend30d=st.floats(min_value=0.0, max_value=10000.0),
    revenue30d=st.floats(min_value=0.0, max_value=100000.0),
    unitsSold30d=st.integers(min_value=0, max_value=10000),
    returns30d=st.integers(min_value=0, max_value=1000),
    currentMargin=st.floats(min_value=-100.0, max_value=100.0),
    marginTrend=st.sampled_from(['up', 'down', 'stable']),
    salesVelocity=st.floats(min_value=0.0, max_value=1000.0),
    acos=st.floats(min_value=0.0, max_value=200.0),
    lastUpdated=st.text(min_size=1)
)

# Feature: marginguard-ai-mvp, Property 1: Risk Score Bounds
@given(sku_strategy)
def test_risk_score_bounds(sku: SKUBase):
    score, factors = calculate_risk(sku)
    assert 0 <= score <= 100
    assert len(factors) == 4 # Margin trend, ad efficiency, fee impact, return rate

# Unit test for specific scenario
def test_high_risk_sku_threshold():
    """Test that a SKU with high ACOS, declining margin, high fees gets a High Risk rating"""
    sku = SKUBase(
        id="TEST1", name="Test Item", asin="B000",
        currentPrice=100.0, cogs=20.0,
        fbaFees=30.0, referralFees=20.0, # 50% fees => (100) * 0.2 = 20
        adSpend30d=1000.0, revenue30d=1500.0,
        unitsSold30d=100, returns30d=20, # 20% returns => (100) * 0.1 = 10
        currentMargin=10.0, marginTrend='down', # Down => 100 * 0.4 = 40
        salesVelocity=3.3, acos=60.0, lastUpdated="2023-01-01" # Acos 60 => 100 * 0.3 = 30
    )
    # Total score should be ~ 40 + 30 + 20 + 10 = 100
    score, factors = calculate_risk(sku)
    
    assert score >= 99.0
    assert get_risk_level(score) == "high"
    
def test_low_risk_sku():
    """Test that optimal SKU metrics evaluate to approximately zero."""
    sku = SKUBase(
        id="TEST2", name="Test Good Item", asin="B001",
        currentPrice=100.0, cogs=20.0,
        fbaFees=10.0, referralFees=10.0, # 20% fees => 0 impact
        adSpend30d=10.0, revenue30d=1500.0,
        unitsSold30d=100, returns30d=0, # 0% returns => 0 impact
        currentMargin=50.0, marginTrend='up', # up => 0 impact
        salesVelocity=10.0, acos=10.0, lastUpdated="2023-01-01" # 10% acos => 0 impact
    )
    score, factors = calculate_risk(sku)
    assert score == 0.0
    assert get_risk_level(score) == "low"

import { SKU } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const ApiService = {
    /**
     * Fetch all SKUs from the backend and enrich with risk scores
     */
    async getSkus(): Promise<SKU[]> {
        try {
            const response = await fetch(`${API_BASE}/skus/`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data: any[] = await response.json();

            // The backend returns SKUBase (no riskScore/riskLevel).
            // Compute them client-side by calling /risk-score for each,
            // or calculate locally to avoid N+1 requests.
            return data.map(sku => {
                const riskResult = computeLocalRisk(sku);
                return {
                    ...sku,
                    riskScore: riskResult.score,
                    riskLevel: riskResult.level,
                } as SKU;
            });
        } catch (e) {
            console.warn("Backend SKU fetch failed, falling back to mock", e);
            return getMockSkus();
        }
    },

    /**
     * Get an AI explanation for a specific SKU's risk factors
     */
    async getExplanation(skuData: any): Promise<{ explanation: string; factors: any[] }> {
        try {
            const response = await fetch(`${API_BASE}/explanation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(skuData)
            });

            if (!response.ok) throw new Error('Failed to fetch AI explanation');

            const data = await response.json();
            return {
                explanation: data.explanation || data.insights,
                factors: data.riskFactors || data.key_factors || []
            };
        } catch (e) {
            console.error("Explanation fetch error:", e);
            return {
                explanation: "AI service currently unavailable. This SKU shows margin pressure outperforming historical averages but is negatively impacted by recent fee changes.",
                factors: [
                    { name: "Margin Trend", impact: 85, severity: "high", dataPoint: "Declining margins over 30 days" },
                    { name: "FBA Fees", impact: 40, severity: "medium", dataPoint: "Fees increased 5%" }
                ]
            };
        }
    },

    /**
     * Simulate a price change using the What-If Engine
     */
    async simulatePrice(skuData: any, newPrice: number): Promise<any> {
        try {
            // Backend expects: { skuId, newPrice, skuData } (camelCase)
            const payload = {
                skuId: skuData.id,
                newPrice: newPrice,
                skuData: skuData
            };

            const response = await fetch(`${API_BASE}/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errBody = await response.text();
                console.error('Simulation API error:', errBody);
                throw new Error(`Simulation failed: ${response.status}`);
            }

            const data = await response.json();
            // Backend returns: { before: {...}, after: {...} }
            // Normalise to shape that SkuDetailDrawer expects
            return {
                projected_margin: data.after?.margin ?? data.projected_margin,
                projected_risk_score: data.after?.riskScore ?? data.projected_risk_score,
                volume_impact_percent: data.after?.estimatedVolumeChange ?? data.volume_impact_percent
            };
        } catch (e) {
            console.error("Simulation error:", e);
            // Local fallback using simple price-elasticity model
            const priceDiff = newPrice - skuData.currentPrice;
            const pricePercentChange = priceDiff / skuData.currentPrice;
            const elasticity = -0.8;
            const volumeChange = pricePercentChange * elasticity;
            const newMargin = ((newPrice - skuData.cogs - skuData.fbaFees - skuData.referralFees) / newPrice) * 100;

            return {
                projected_margin: newMargin,
                projected_risk_score: newMargin < 20 ? 80 : newMargin > 40 ? 20 : 50,
                volume_impact_percent: volumeChange * 100
            };
        }
    }
};

// Fallback Mock Data
function getMockSkus(): SKU[] {
    return [
        {
            id: "SKU001", name: "Premium Yoga Mat", asin: "B08XYZ1234",
            currentPrice: 39.99, cogs: 12.50, fbaFees: 5.20, referralFees: 6.00,
            adSpend30d: 450, revenue30d: 2800, unitsSold30d: 70, returns30d: 3,
            currentMargin: 40.7, marginTrend: 'stable', riskScore: 32, riskLevel: 'low',
            salesVelocity: 2.3, acos: 16.0, lastUpdated: new Date().toISOString()
        },
        {
            id: "SKU002", name: "Wireless Earbuds Pro", asin: "B09ABC5678",
            currentPrice: 89.99, cogs: 45.00, fbaFees: 3.50, referralFees: 13.50,
            adSpend30d: 1200, revenue30d: 8500, unitsSold30d: 94, returns30d: 12,
            currentMargin: 31.1, marginTrend: 'down', riskScore: 78, riskLevel: 'high',
            salesVelocity: 3.1, acos: 14.1, lastUpdated: new Date().toISOString()
        },
        {
            id: "SKU003", name: "Stainless Steel Water Bottle", asin: "B07DEF9012",
            currentPrice: 24.99, cogs: 8.00, fbaFees: 4.80, referralFees: 3.75,
            adSpend30d: 300, revenue30d: 3700, unitsSold30d: 148, returns30d: 5,
            currentMargin: 33.7, marginTrend: 'up', riskScore: 45, riskLevel: 'medium',
            salesVelocity: 4.9, acos: 8.1, lastUpdated: new Date().toISOString()
        },
        {
            id: "SKU004", name: "Ergonomic Desk Chair", asin: "B01GHI3456",
            currentPrice: 199.99, cogs: 85.00, fbaFees: 24.50, referralFees: 30.00,
            adSpend30d: 800, revenue30d: 6000, unitsSold30d: 30, returns30d: 4,
            currentMargin: 30.2, marginTrend: 'down', riskScore: 65, riskLevel: 'medium',
            salesVelocity: 1.0, acos: 13.3, lastUpdated: new Date().toISOString()
        },
        {
            id: "SKU005", name: "Resistance Bands Set", asin: "B02JKL7890",
            currentPrice: 19.99, cogs: 4.50, fbaFees: 3.20, referralFees: 3.00,
            adSpend30d: 500, revenue30d: 4000, unitsSold30d: 200, returns30d: 15,
            currentMargin: 46.5, marginTrend: 'down', riskScore: 82, riskLevel: 'high',
            salesVelocity: 6.6, acos: 12.5, lastUpdated: new Date().toISOString()
        }
    ];
}

/**
 * Client-side risk calculation mirroring the backend's risk_engine.py weights.
 * This avoids N+1 API calls when enriching the SKU list.
 */
function computeLocalRisk(sku: any): { score: number; level: 'low' | 'medium' | 'high' } {
    // 1. Margin Trend (40%)
    let marginScore = 30; // stable
    if (sku.marginTrend === 'up') marginScore = 0;
    else if (sku.marginTrend === 'down') marginScore = 100;

    // 2. Ad Efficiency (30%) — ACOS
    let adScore = 0;
    if (sku.acos > 50) adScore = 100;
    else if (sku.acos < 15) adScore = 0;
    else adScore = ((sku.acos - 15) / (50 - 15)) * 100;

    // 3. Fee Impact (20%)
    const feePct = sku.currentPrice > 0
        ? ((sku.fbaFees + sku.referralFees) / sku.currentPrice) * 100
        : 100;
    let feeScore = 0;
    if (feePct > 45) feeScore = 100;
    else if (feePct < 25) feeScore = 0;
    else feeScore = ((feePct - 25) / (45 - 25)) * 100;

    // 4. Return Rate (10%)
    const returnRate = sku.unitsSold30d > 0
        ? (sku.returns30d / sku.unitsSold30d) * 100
        : 0;
    let retScore = 0;
    if (returnRate > 10) retScore = 100;
    else if (returnRate < 2) retScore = 0;
    else retScore = ((returnRate - 2) / (10 - 2)) * 100;

    const score = Math.max(0, Math.min(100,
        marginScore * 0.4 + adScore * 0.3 + feeScore * 0.2 + retScore * 0.1
    ));

    const level: 'low' | 'medium' | 'high' = score <= 39 ? 'low' : score <= 69 ? 'medium' : 'high';
    return { score: Math.round(score * 10) / 10, level };
}

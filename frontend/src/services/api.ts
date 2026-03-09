import { SKU } from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

export const ApiService = {
    /**
     * Fetch all SKUs from the mock database
     */
    async getSkus(): Promise<SKU[]> {
        try {
            // In a real app we would call an endpoint here.
            // For this MVP (since the FASTAPI backend serves specific mock files via raw_data or handles risk-score generation),
            // we'll fetch from the intelligence/raw data endpoints if available, or simulate if not fully wired.

            // Attempt to hit the backend raw data if it exists:
            const response = await fetch(`${API_BASE}/raw-data/skus.json`);
            if (response.ok) {
                const data = await response.json();
                return data.skus || data;
            }
            throw new Error("Unable to fetch real SKUs");
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

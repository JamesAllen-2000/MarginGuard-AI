export interface SKU {
    id: string;                    // Unique identifier
    name: string;                  // Product name
    asin: string;                  // Amazon Standard Identification Number
    currentPrice: number;          // Current selling price
    cogs: number;                  // Cost of goods sold
    fbaFees: number;              // Fulfillment fees
    referralFees: number;         // Amazon referral fees
    adSpend30d: number;           // Ad spend last 30 days
    revenue30d: number;           // Revenue last 30 days
    unitsSold30d: number;         // Units sold last 30 days
    returns30d: number;           // Return count last 30 days
    currentMargin: number;        // Current profit margin %
    marginTrend: 'up' | 'down' | 'stable';
    riskScore: number;            // 0-100 risk score
    riskLevel: 'low' | 'medium' | 'high';
    salesVelocity: number;        // Units per day
    acos: number;                 // Advertising Cost of Sale %
    lastUpdated: string;          // ISO timestamp
}

export interface RiskFactor {
    name: string;                 // Factor name (e.g., "Declining Margin")
    impact: number;               // Contribution to risk score (0-100)
    dataPoint: string;            // Specific metric (e.g., "Margin down 15% in 30 days")
    severity: 'low' | 'medium' | 'high';
}

export interface SimulationResult {
    before: {
        price: number;
        margin: number;
        riskScore: number;
        projectedRevenue30d: number;
    };
    after: {
        price: number;
        margin: number;
        riskScore: number;
        projectedRevenue30d: number;
        estimatedVolumeChange: number;  // Percentage change
    };
    recommendation: string;       // AI-generated recommendation
}

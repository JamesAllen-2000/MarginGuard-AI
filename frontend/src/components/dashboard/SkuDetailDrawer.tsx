import { FC, useState, useEffect } from 'react';
import { GlassPanel } from '../layout/GlassPanel';
import { SKU } from '../../types';
import { ApiService } from '../../services/api';
import { X, TrendingUp, AlertTriangle, AlertCircle, RefreshCw } from 'lucide-react';

interface SkuDetailDrawerProps {
    sku: SKU | null;
    onClose: () => void;
}

export const SkuDetailDrawer: FC<SkuDetailDrawerProps> = ({ sku, onClose }) => {
    const [loading, setLoading] = useState(false);
    const [explanation, setExplanation] = useState<{ explanation: string; factors: any[] } | null>(null);

    // Simulation State
    const [simPrice, setSimPrice] = useState<number>(0);
    const [simulating, setSimulating] = useState(false);
    const [simResult, setSimResult] = useState<any>(null);

    useEffect(() => {
        if (sku) {
            setSimPrice(sku.currentPrice);
            setExplanation(null);
            setSimResult(null);
            loadExplanation();
        }
    }, [sku]);

    const loadExplanation = async () => {
        if (!sku) return;
        setLoading(true);
        try {
            const result = await ApiService.getExplanation(sku);
            setExplanation(result);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSimulate = async () => {
        if (!sku) return;
        setSimulating(true);
        try {
            const result = await ApiService.simulatePrice(sku, simPrice);
            setSimResult({
                ...result,
                projectedMargin: result.projected_margin || result.after?.margin,
                projectedRisk: result.projected_risk_score || result.after?.riskScore,
                volumeImpact: result.volume_impact_percent || result.after?.estimatedVolumeChange
            });
        } catch (err) {
            console.error(err);
        } finally {
            setSimulating(false);
        }
    };

    if (!sku) return null;

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Header Info */}
            <GlassPanel style={{ position: 'relative' }}>
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute', top: '16px', right: '16px',
                        background: 'rgba(255,255,255,0.1)', border: 'none',
                        borderRadius: '50%', width: '32px', height: '32px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: 'white', cursor: 'pointer', transition: 'background 0.2s'
                    }}
                >
                    <X size={18} />
                </button>

                <span style={{
                    background: sku.riskLevel === 'high' ? 'var(--risk-high-bg)' :
                        sku.riskLevel === 'medium' ? 'var(--risk-medium-bg)' : 'var(--risk-low-bg)',
                    color: sku.riskLevel === 'high' ? 'var(--risk-high)' :
                        sku.riskLevel === 'medium' ? 'var(--risk-medium)' : 'var(--risk-low)',
                    padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600,
                    textTransform: 'uppercase', marginBottom: '8px', display: 'inline-block'
                }}>
                    {sku.riskLevel} Risk • {sku.riskScore}/100
                </span>

                <h2 style={{ margin: '0 0 8px 0', fontSize: '1.5rem', paddingRight: '30px' }}>{sku.name}</h2>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>ASIN: {sku.asin}</div>

                <div style={{ display: 'flex', gap: '2rem', marginTop: '1.5rem' }}>
                    <div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Margin</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{sku.currentMargin.toFixed(1)}%</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Price</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>${sku.currentPrice.toFixed(2)}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Velocity</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{sku.salesVelocity}/d</div>
                    </div>
                </div>
            </GlassPanel>

            {/* AI Explanation */}
            <GlassPanel style={{ flex: 1, borderTop: '4px solid var(--accent)' }}>
                <h3 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TrendingUp size={20} className="text-blue-400" />
                    AI Risk Analysis
                </h3>

                {loading ? (
                    <div style={{ display: 'flex', gap: '8px', color: 'var(--text-secondary)', alignItems: 'center', padding: '2rem 0', justifyContent: 'center' }}>
                        <RefreshCw size={20} className="animate-spin" /> Fetching Bedrock Analysis...
                    </div>
                ) : explanation ? (
                    <div>
                        <p style={{ lineHeight: 1.6, color: 'var(--text-primary)', background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px', borderLeft: '3px solid var(--accent)' }}>
                            {explanation.explanation}
                        </p>

                        <div style={{ marginTop: '1.5rem' }}>
                            <h4 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '12px' }}>
                                Key Contributing Factors
                            </h4>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                {explanation.factors.map((factor, idx) => (
                                    <div key={idx} style={{
                                        display: 'flex', gap: '12px', alignItems: 'flex-start',
                                        background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px'
                                    }}>
                                        {factor.severity === 'high' ? <AlertTriangle size={18} color="var(--risk-high)" /> : <AlertCircle size={18} color="var(--risk-medium)" />}
                                        <div>
                                            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{factor.name}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{factor.dataPoint || "Significantly impacts risk probability"}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div style={{ color: 'var(--text-secondary)' }}>Unable to load analysis.</div>
                )}
            </GlassPanel>

            {/* Price Simulator */}
            <GlassPanel>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem' }}>Pricing Strategy Simulator</h3>

                <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Test New Price</span>
                        <span style={{ fontWeight: 600 }}>${simPrice.toFixed(2)}</span>
                    </div>
                    <input
                        type="range"
                        min={sku.currentPrice * 0.5}
                        max={sku.currentPrice * 1.5}
                        step={0.5}
                        value={simPrice}
                        onChange={(e) => setSimPrice(parseFloat(e.target.value))}
                        style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--accent)' }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        <span>-50%</span>
                        <span>Current (${sku.currentPrice})</span>
                        <span>+50%</span>
                    </div>
                </div>

                <button
                    className="btn"
                    onClick={handleSimulate}
                    disabled={simulating || simPrice === sku.currentPrice}
                    style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px', opacity: (simulating || simPrice === sku.currentPrice) ? 0.5 : 1 }}
                >
                    {simulating ? <RefreshCw className="animate-spin" size={18} /> : 'Run Elasticity Simulation'}
                </button>

                {simResult && (
                    <div style={{
                        marginTop: '1.5rem', padding: '16px', background: 'rgba(59, 130, 246, 0.1)',
                        border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: '8px'
                    }}>
                        <h4 style={{ margin: '0 0 12px 0', fontSize: '0.875rem', color: '#93c5fd' }}>Projected Outcomes</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>New Margin</div>
                                <div style={{
                                    fontSize: '1.125rem', fontWeight: 600,
                                    color: simResult.projectedMargin > sku.currentMargin ? 'var(--risk-low)' : 'var(--risk-high)'
                                }}>
                                    {simResult.projectedMargin.toFixed(1)}%
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Risk Score</div>
                                <div style={{
                                    fontSize: '1.125rem', fontWeight: 600,
                                    color: simResult.projectedRisk < sku.riskScore ? 'var(--risk-low)' : (simResult.projectedRisk > 70 ? 'var(--risk-high)' : 'var(--text-primary)')
                                }}>
                                    {Math.round(simResult.projectedRisk)} / 100
                                </div>
                            </div>
                            <div style={{ gridColumn: '1 / -1' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Est. Volume Impact</div>
                                <div style={{
                                    fontSize: '0.875rem', fontWeight: 500,
                                    color: simResult.volumeImpact > 0 ? 'var(--risk-low)' : 'var(--risk-high)'
                                }}>
                                    {simResult.volumeImpact > 0 ? '+' : ''}{simResult.volumeImpact.toFixed(1)}% daily units
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </GlassPanel>
        </div>
    );
};

import { FC } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { GlassPanel } from '../layout/GlassPanel';
import { SKU } from '../../types';

interface ProfitHealthRadarProps {
    skus: SKU[];
    onSkuClick: (sku: SKU) => void;
}

export const ProfitHealthRadar: FC<ProfitHealthRadarProps> = ({ skus, onSkuClick }) => {
    // Map risk levels to colors
    const getRiskColor = (score: number) => {
        if (score >= 70) return '#ef4444'; // Red
        if (score >= 40) return '#f59e0b'; // Yellow
        return '#10b981'; // Green
    };

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload as SKU;
            return (
                <div style={{
                    background: 'rgba(15, 23, 42, 0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    padding: '12px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                    color: 'white'
                }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>{data.name}</h4>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                        <div>Margin: <span style={{ color: 'white' }}>{data.currentMargin}%</span></div>
                        <div>Velocity: <span style={{ color: 'white' }}>{data.salesVelocity} units/day</span></div>
                        <div style={{
                            marginTop: '4px',
                            paddingTop: '4px',
                            borderTop: '1px solid rgba(255,255,255,0.1)',
                            color: getRiskColor(data.riskScore)
                        }}>
                            Risk Score: {data.riskScore}/100
                        </div>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <GlassPanel>
            <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '1.25rem', margin: 0 }}>Profit Health Radar</h2>
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981' }}></span> Low Risk
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b' }}></span> Warning
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#ef4444' }}></span> Critical
                    </div>
                </div>
            </div>

            <div style={{ height: '400px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis
                            type="number"
                            dataKey="currentMargin"
                            name="Profit Margin"
                            unit="%"
                            stroke="#64748b"
                            tick={{ fill: '#64748b' }}
                            domain={['auto', 'auto']}
                        />
                        <YAxis
                            type="number"
                            dataKey="salesVelocity"
                            name="Sales Velocity"
                            unit="/day"
                            stroke="#64748b"
                            tick={{ fill: '#64748b' }}
                        />
                        {/* ZAxis determines bubble size based on revenue */}
                        <ZAxis type="number" dataKey="revenue30d" range={[100, 500]} />
                        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: 'rgba(255,255,255,0.1)' }} />

                        <Scatter
                            name="SKUs"
                            data={skus}
                            onClick={(data) => onSkuClick(data.payload || data)}
                            style={{ cursor: 'pointer' }}
                        >
                            {skus.map((sku, index) => (
                                <Cell key={`cell-${index}`} fill={getRiskColor(sku.riskScore)} fillOpacity={0.7} />
                            ))}
                        </Scatter>
                    </ScatterChart>
                </ResponsiveContainer>
            </div>
        </GlassPanel>
    );
};

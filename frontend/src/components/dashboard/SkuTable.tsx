import { FC, useState } from 'react';
import { GlassPanel } from '../layout/GlassPanel';
import { SKU } from '../../types';
import { ArrowDown, ArrowUp, Minus } from 'lucide-react';

interface SkuTableProps {
    skus: SKU[];
    onRowClick: (sku: SKU) => void;
}

export const SkuTable: FC<SkuTableProps> = ({ skus, onRowClick }) => {
    const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
    const [sortField, setSortField] = useState<keyof SKU>('riskScore');
    const [sortDesc, setSortDesc] = useState(true);

    const handleSort = (field: keyof SKU) => {
        if (sortField === field) {
            setSortDesc(!sortDesc);
        } else {
            setSortField(field);
            setSortDesc(true);
        }
    };

    const filteredSkus = skus.filter(sku => {
        if (filter === 'all') return true;
        return sku.riskLevel === filter;
    });

    const sortedSkus = [...filteredSkus].sort((a, b) => {
        const aVal = a[sortField];
        const bVal = b[sortField];

        if (typeof aVal === 'string' && typeof bVal === 'string') {
            return sortDesc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
        }

        return sortDesc ? (bVal as number) - (aVal as number) : (aVal as number) - (bVal as number);
    });

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'up': return <ArrowUp size={16} className="text-green-500" />;
            case 'down': return <ArrowDown size={16} className="text-red-500" />;
            default: return <Minus size={16} className="text-gray-400" />;
        }
    };

    return (
        <GlassPanel>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0 }}>SKU Directory</h2>

                <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(0,0,0,0.2)', padding: '4px', borderRadius: '8px' }}>
                    {['all', 'high', 'medium', 'low'].map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f as any)}
                            style={{
                                background: filter === f ? 'var(--accent)' : 'transparent',
                                color: filter === f ? 'white' : 'var(--text-secondary)',
                                border: 'none',
                                padding: '4px 12px',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                textTransform: 'capitalize',
                                fontSize: '0.875rem',
                                transition: 'all 0.2s'
                            }}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                            <th style={{ padding: '12px', cursor: 'pointer' }} onClick={() => handleSort('name')}>Product</th>
                            <th style={{ padding: '12px', cursor: 'pointer' }} onClick={() => handleSort('currentMargin')}>Margin</th>
                            <th style={{ padding: '12px', cursor: 'pointer' }} onClick={() => handleSort('marginTrend')}>Trend</th>
                            <th style={{ padding: '12px', cursor: 'pointer' }} onClick={() => handleSort('salesVelocity')}>Velocity</th>
                            <th style={{ padding: '12px', cursor: 'pointer' }} onClick={() => handleSort('acos')}>AcoS</th>
                            <th style={{ padding: '12px', cursor: 'pointer' }} onClick={() => handleSort('riskScore')}>Risk Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedSkus.map((sku) => (
                            <tr
                                key={sku.id}
                                onClick={() => onRowClick(sku)}
                                style={{
                                    borderBottom: '1px solid rgba(255,255,255,0.05)',
                                    cursor: 'pointer',
                                    transition: 'background 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            >
                                <td style={{ padding: '16px 12px' }}>
                                    <div style={{ fontWeight: 500 }}>{sku.name}</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{sku.asin} • ${sku.currentPrice}</div>
                                </td>
                                <td style={{ padding: '16px 12px', fontWeight: 500 }}>
                                    <span style={{ color: sku.currentMargin < 30 ? 'var(--risk-high)' : 'var(--text-primary)' }}>
                                        {sku.currentMargin}%
                                    </span>
                                </td>
                                <td style={{ padding: '16px 12px' }}>{getTrendIcon(sku.marginTrend)}</td>
                                <td style={{ padding: '16px 12px' }}>{sku.salesVelocity} /d</td>
                                <td style={{ padding: '16px 12px' }}>{sku.acos}%</td>
                                <td style={{ padding: '16px 12px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <div style={{
                                            width: '100%',
                                            height: '6px',
                                            background: 'rgba(255,255,255,0.1)',
                                            borderRadius: '3px',
                                            overflow: 'hidden'
                                        }}>
                                            <div style={{
                                                height: '100%',
                                                width: `${sku.riskScore}%`,
                                                background: sku.riskLevel === 'high' ? 'var(--risk-high)' :
                                                    sku.riskLevel === 'medium' ? 'var(--risk-medium)' : 'var(--risk-low)'
                                            }} />
                                        </div>
                                        <span style={{ fontSize: '0.875rem', fontWeight: 600, width: '28px', textAlign: 'right' }}>
                                            {sku.riskScore}
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </GlassPanel>
    );
};

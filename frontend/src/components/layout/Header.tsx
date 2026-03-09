import { FC } from 'react';
import { GlassPanel } from './GlassPanel';

export const Header: FC = () => {
    return (
        <header style={{ marginBottom: '2rem' }}>
            <GlassPanel className="header-panel" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1rem 2rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 'bold',
                        fontSize: '1.2rem',
                        boxShadow: '0 4px 12px rgba(59, 130, 246, 0.5)'
                    }}>
                        M
                    </div>
                    <h1 className="text-gradient" style={{ margin: 0, fontSize: '1.5rem' }}>
                        MarginGuard AI
                    </h1>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        Demo Mode Active
                    </div>
                    <button className="btn btn-glass" style={{ borderRadius: '20px', padding: '0.5rem 1.25rem' }}>
                        Alex Seller
                    </button>
                </div>
            </GlassPanel>
        </header>
    );
};

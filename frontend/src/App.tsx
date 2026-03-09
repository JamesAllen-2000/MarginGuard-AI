import { useState, useEffect } from 'react';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { ProfitHealthRadar } from './components/dashboard/ProfitHealthRadar';
import { SkuTable } from './components/dashboard/SkuTable';
import { SkuDetailDrawer } from './components/dashboard/SkuDetailDrawer';
import { ApiService } from './services/api';
import { SKU } from './types';
import { RefreshCw } from 'lucide-react';

function App() {
  const [skus, setSkus] = useState<SKU[]>([]);
  const [selectedSku, setSelectedSku] = useState<SKU | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSkus = async () => {
      setLoading(true);
      try {
        const data = await ApiService.getSkus();
        setSkus(data);
      } catch (e) {
        console.error("Failed to load SKUs", e);
      } finally {
        setLoading(false);
      }
    };

    fetchSkus();
  }, []);

  return (
    <DashboardLayout sidebar={selectedSku ? (
      <SkuDetailDrawer sku={selectedSku} onClose={() => setSelectedSku(null)} />
    ) : null}>

      {loading ? (
        <div style={{ height: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)' }}>
          <RefreshCw className="animate-spin" size={32} />
        </div>
      ) : skus.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <ProfitHealthRadar skus={skus} onSkuClick={setSelectedSku} />
          <SkuTable skus={skus} onRowClick={setSelectedSku} />
        </div>
      ) : (
        <div style={{ height: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
          No SKU data available. Check backend connection.
        </div>
      )}

    </DashboardLayout>
  );
}

export default App;

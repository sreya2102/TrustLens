import { Shield } from 'lucide-react';

function App() {
  return (
    <div style={{ padding: '24px', maxWidth: '600px', margin: '0 auto', color: 'var(--text-light)', fontFamily: 'Inter, sans-serif' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <Shield size={32} color="var(--primary)" />
        <h1 style={{ color: 'var(--primary)', margin: 0 }}>TrustLens Options</h1>
      </div>
      <div style={{ backgroundColor: 'var(--bg-card)', padding: '24px', borderRadius: '12px' }}>
        <p>TrustLens settings will be configured here.</p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Currently running on first milestone foundation (No ML integration yet).</p>
      </div>
    </div>
  );
}

export default App;

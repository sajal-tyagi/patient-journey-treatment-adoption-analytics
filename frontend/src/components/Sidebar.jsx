import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';

const NAV = [
  { id: 'overview',        label: 'Overview',           icon: '📊' },
  { id: 'journey',         label: 'Patient Journey',    icon: '🏥' },
  { id: 'adoption',        label: 'Treatment Adoption', icon: '💊' },
  { id: 'segments',        label: 'Patient Segments',   icon: '👥' },
  { id: 'market',          label: 'Market Opportunity', icon: '🗺️' },
  { id: 'model',           label: 'Model Insights',     icon: '🤖' },
  { id: 'about',           label: 'About',              icon: 'ℹ️' },
];

export default function Sidebar({ page, setPage }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    api.health()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('error'));
  }, []);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>Patient Analytics</h1>
        <p>Therapy X · NovaCure</p>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-label">Analytics</div>
        {NAV.map(n => (
          <button
            key={n.id}
            className={`nav-item ${page === n.id ? 'active' : ''}`}
            onClick={() => setPage(n.id)}
          >
            <span className="nav-icon">{n.icon}</span>
            <span>{n.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
          <span style={{
            width: 7, height: 7, borderRadius: '50%', display: 'inline-block',
            background: status === 'ok' ? '#22c55e' : status === 'error' ? '#ef4444' : '#94a3b8',
            flexShrink: 0,
          }} />
          API {status === 'ok' ? 'Connected' : status === 'error' ? 'Offline' : 'Connecting…'}
        </p>
        <p>Synthetic Data</p>
        <p>Analytics Portfolio</p>
      </div>
    </aside>
  );
}

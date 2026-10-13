import React, { useState } from 'react';
import { Play, Sparkles, Zap, Globe, AlertOctagon } from 'lucide-react';
import { transactionsApi } from '../api/client';

export default function ScenarioBar({ onTriggered }) {
  const [running, setRunning] = useState(null);

  const scenarios = [
    { id: 'normal', label: 'Normal ($45)', icon: Sparkles, desc: 'Baseline safe purchase' },
    { id: 'high_amount', label: 'High Amount ($7.8k)', icon: Zap, desc: 'Triggers Rule A (+25 pts)' },
    { id: 'velocity_burst', label: 'Velocity Burst (4x)', icon: Play, desc: 'Triggers Rule B (+20 pts)' },
    { id: 'location_mismatch', label: 'Location Jump (SG)', icon: Globe, desc: 'Triggers Rule F (+20 pts)' },
    { id: 'critical_combo', label: 'Critical Combo (85+)', icon: AlertOctagon, desc: 'Triggers Multi-Rule High/Critical' }
  ];

  const handleRun = async (scenarioId) => {
    try {
      setRunning(scenarioId);
      const res = await transactionsApi.triggerScenario(scenarioId);
      if (onTriggered) onTriggered(res);
    } catch (err) {
      alert(`Scenario failed: ${err.message}`);
    } finally {
      setRunning(null);
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      overflowX: 'auto',
      padding: '4px 0'
    }}>
      <span style={{
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        whiteSpace: 'nowrap'
      }}>
        Demo Scenarios:
      </span>
      {scenarios.map(s => {
        const Icon = s.icon;
        const isCurrent = running === s.id;
        return (
          <button
            key={s.id}
            onClick={() => handleRun(s.id)}
            disabled={running !== null}
            className="button button-secondary button-sm"
            title={s.desc}
            style={{
              whiteSpace: 'nowrap',
              backgroundColor: s.id === 'critical_combo' ? 'rgba(239, 68, 68, 0.1)' : 'var(--bg-card)',
              borderColor: s.id === 'critical_combo' ? 'rgba(239, 68, 68, 0.3)' : 'var(--border-color)',
              color: s.id === 'critical_combo' ? 'var(--risk-critical)' : 'var(--text-main)'
            }}
          >
            <Icon size={13} />
            <span>{isCurrent ? 'Generating...' : s.label}</span>
          </button>
        );
      })}
    </div>
  );
}

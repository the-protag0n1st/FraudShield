import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  DollarSign, 
  AlertTriangle, 
  Activity, 
  ArrowUpRight, 
  Briefcase,
  TrendingUp,
  Clock
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import { dashboardApi, transactionsApi } from '../api/client';
import StatCard from '../components/StatCard';
import RiskBadge from '../components/RiskBadge';
import TransactionDrawer from '../components/TransactionDrawer';
import ScenarioBar from '../components/ScenarioBar';

export default function OverviewPage() {
  const [data, setData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTxn, setSelectedTxn] = useState(null);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const [sumRes, trendRes] = await Promise.all([
        dashboardApi.getSummary(),
        dashboardApi.getTrends()
      ]);
      setData(sumRes);
      setTrends(trendRes.trends || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleInspect = async (id) => {
    try {
      const res = await transactionsApi.getTransaction(id);
      setSelectedTxn(res.transaction);
    } catch (err) {
      alert(`Failed to load transaction: ${err.message}`);
    }
  };

  if (loading && !data) {
    return <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading dashboard metrics...</div>;
  }

  if (error) {
    return <div style={{ padding: '40px', color: 'var(--risk-critical)' }}>Failed to load dashboard: {error}</div>;
  }

  const s = data?.summary || {};

  return (
    <div className="content-body">
      {/* Top Banner with Demo Trigger Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        backgroundColor: 'var(--bg-card)',
        padding: '16px 20px',
        borderRadius: '12px',
        border: '1px solid var(--border-color)'
      }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Real-Time Risk Monitoring</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Continuous ingestion and deterministic fraud heuristics running on MySQL 8 InnoDB.
          </p>
        </div>
        <ScenarioBar onTriggered={() => loadDashboard()} />
      </div>

      {/* KPI Stats Grid */}
      <div className="stats-grid">
        <StatCard 
          title="Total Processed" 
          value={`$${Number(s.total_volume || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          subtext={`${s.total_transactions} total transactions`}
          icon={DollarSign}
        />
        <StatCard 
          title="Flagged Transactions" 
          value={s.flagged_transactions}
          subtext={`${s.fraud_rate}% fraud detection rate`}
          icon={AlertTriangle}
          alert={s.flagged_transactions > 0}
        />
        <StatCard 
          title="Critical Alerts" 
          value={s.critical_transactions}
          subtext="Scores 80-100 requiring immediate review"
          icon={ShieldAlert}
          alert={s.critical_transactions > 0}
        />
        <StatCard 
          title="Pending Cases" 
          value={s.pending_cases}
          subtext={`${s.confirmed_fraud_cases} confirmed fraud resolutions`}
          icon={Briefcase}
        />
      </div>

      {/* Transaction & Risk Trends Chart */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <TrendingUp size={18} color="var(--accent-blue)" />
            <span>Transaction Volume & Flagged Activity Trends</span>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Aggregation across recent timestamps
          </span>
        </div>

        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <AreaChart data={trends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="totalVolume" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                </linearGradient>
                <linearGradient id="flaggedVolume" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.5}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#111827', 
                  borderColor: '#334155', 
                  borderRadius: '8px',
                  color: '#f8fafc',
                  fontSize: '0.85rem'
                }} 
              />
              <Area type="monotone" dataKey="total_count" stroke="#3b82f6" fillOpacity={1} fill="url(#totalVolume)" name="Total Txns" />
              <Area type="monotone" dataKey="flagged_count" stroke="#ef4444" fillOpacity={1} fill="url(#flaggedVolume)" name="Flagged (≥ 60)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2-Column Split: Recent Flagged & Recent Case Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '20px' }}>
        {/* Recent Flagged Transactions */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <ShieldAlert size={18} color="var(--risk-critical)" />
              <span>Recent High & Critical Flagged Transactions</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {data?.recent_flagged?.map((t) => (
              <div 
                key={t.id}
                onClick={() => handleInspect(t.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 14px',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'background-color 0.15s ease'
                }}
                className="hover-card"
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{t.customer_name}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>• {t.merchant_name}</span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    ${Number(t.amount).toFixed(2)} {t.currency} • {t.location} ({t.country_code})
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <RiskBadge score={t.risk_score} level={t.risk_level} />
                  <ArrowUpRight size={16} color="var(--text-muted)" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Investigation Activity */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Clock size={18} color="var(--accent-cyan)" />
              <span>Recent Investigator Activity</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {data?.recent_activity?.map((a) => (
              <div 
                key={a.id}
                style={{
                  padding: '12px 14px',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-blue)' }}>
                    {a.author_name}
                  </span>
                  <span className={`status-badge status-${a.case_status}`}>
                    {a.case_status}
                  </span>
                </div>
                <p style={{ fontSize: '0.83rem', color: 'var(--text-main)', marginBottom: '6px', lineHeight: '1.4' }}>
                  "{a.note_text}"
                </p>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Case #{a.case_id} ({a.transaction_reference})</span>
                  <span>{new Date(a.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Slide-out Inspector Drawer */}
      <TransactionDrawer 
        transaction={selectedTxn}
        onClose={() => setSelectedTxn(null)}
        onReassess={async (id) => {
          await transactionsApi.reassess(id);
          handleInspect(id);
          loadDashboard();
        }}
      />
    </div>
  );
}

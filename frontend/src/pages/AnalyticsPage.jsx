import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { 
  BarChart3, 
  Store, 
  PieChart as PieIcon, 
  CreditCard, 
  CheckCircle, 
  ShieldAlert 
} from 'lucide-react';
import { analyticsApi } from '../api/client';

const RISK_COLORS = {
  'low': '#10b981',
  'medium': '#f59e0b',
  'high': '#f97316',
  'critical': '#ef4444'
};

const BUCKET_COLORS = ['#10b981', '#f59e0b', '#f97316', '#ef4444'];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [riskDist, setRiskDist] = useState([]);
  const [merchants, setMerchants] = useState([]);
  const [resolutions, setResolutions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        const [oRes, rRes, mRes, resRes] = await Promise.all([
          analyticsApi.getOverview(),
          analyticsApi.getRiskDistribution(),
          analyticsApi.getTopMerchants(),
          analyticsApi.getResolutionRates()
        ]);
        setOverview(oRes);
        setRiskDist(rRes.distribution || []);
        setMerchants(mRes.merchants || []);
        setResolutions(resRes.resolution_rates || []);
      } catch (err) {
        alert(`Failed to load analytics: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading analytics from MySQL views...</div>;
  }

  return (
    <div className="content-body">
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Risk Intelligence & Merchant Analytics</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Database aggregate queries across transactions, heuristic rule distributions, and merchant threat indexes.
        </p>
      </div>

      {/* Grid of Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '20px' }}>
        {/* Risk Score Bucket Distribution */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <BarChart3 size={18} color="var(--accent-blue)" />
              <span>Risk Tier Distribution</span>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Transaction Count by Score Tier</span>
          </div>

          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={riskDist} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
                <XAxis dataKey="score_bucket" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#111827', 
                    borderColor: '#334155', 
                    borderRadius: '8px', 
                    color: '#f8fafc' 
                  }} 
                />
                <Bar dataKey="transaction_count" radius={[6, 6, 0, 0]} name="Transactions">
                  {riskDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={BUCKET_COLORS[index % BUCKET_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Case Resolution Outcomes */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <CheckCircle size={18} color="var(--accent-cyan)" />
              <span>Investigation Case Resolution Rates</span>
            </div>
          </div>

          <div style={{ width: '100%', height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={resolutions}
                  dataKey="count"
                  nameKey="case_status"
                  cx="50%"
                  cy="50%"
                  outerRadius={85}
                  innerRadius={45}
                  paddingAngle={4}
                  label={({ case_status, percentage }) => `${case_status}: ${percentage}%`}
                >
                  {resolutions.map((entry, index) => {
                    const colors = {
                      open: '#3b82f6',
                      investigating: '#f59e0b',
                      resolved_fraud: '#ef4444',
                      resolved_legitimate: '#10b981'
                    };
                    return <Cell key={`cell-${index}`} fill={colors[entry.case_status] || '#64748b'} />;
                  })}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#111827', 
                    borderColor: '#334155', 
                    borderRadius: '8px', 
                    color: '#f8fafc' 
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Merchant Threat Index Table (From v_merchant_risk) */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <Store size={18} color="var(--accent-blue)" />
            <span>Merchant Risk Analysis (Database View: v_merchant_risk)</span>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Ranked by high-risk flags & average heuristic score
          </span>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Merchant Name</th>
                <th>Category</th>
                <th>Total Transactions</th>
                <th>Total Volume</th>
                <th>Flagged Txns (≥ 60)</th>
                <th>Critical Txns</th>
                <th>Avg Risk Score</th>
                <th>Risk Profile</th>
              </tr>
            </thead>
            <tbody>
              {merchants.map(m => {
                const avgScore = Number(m.avg_risk_score || 0);
                return (
                  <tr key={m.merchant_id}>
                    <td style={{ fontWeight: 600 }}>{m.merchant_name}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>{m.category}</td>
                    <td>{m.total_transactions}</td>
                    <td style={{ fontWeight: 500 }}>
                      ${Number(m.total_volume || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{
                      fontWeight: 700,
                      color: m.flagged_count > 0 ? 'var(--risk-high)' : 'var(--text-muted)'
                    }}>
                      {m.flagged_count}
                    </td>
                    <td style={{
                      fontWeight: 700,
                      color: m.critical_count > 0 ? 'var(--risk-critical)' : 'var(--text-muted)'
                    }}>
                      {m.critical_count}
                    </td>
                    <td>
                      <span style={{
                        fontWeight: 700,
                        color: avgScore >= 60 ? 'var(--risk-high)' : avgScore >= 30 ? 'var(--risk-medium)' : 'var(--risk-low)'
                      }}>
                        {avgScore.toFixed(1)} / 100
                      </span>
                    </td>
                    <td>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        padding: '3px 8px',
                        borderRadius: '4px',
                        backgroundColor: avgScore >= 50 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                        color: avgScore >= 50 ? 'var(--risk-critical)' : 'var(--risk-low)'
                      }}>
                        {avgScore >= 50 ? 'Elevated Risk' : 'Standard Risk'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Channel Distribution Grid */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <CreditCard size={18} color="var(--accent-cyan)" />
            <span>Transaction Channel Threat Breakdown</span>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          {overview?.channel_distribution?.map(c => (
            <div key={c.channel} style={{
              padding: '16px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: '8px',
              border: '1px solid var(--border-color)'
            }}>
              <div style={{ textTransform: 'uppercase', fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '6px' }}>
                Channel: {c.channel}
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '4px' }}>
                {c.count} txns
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                ${Number(c.total_amount).toLocaleString()} total volume
              </div>
              <div style={{ fontSize: '0.78rem', color: c.flagged_count > 0 ? 'var(--risk-critical)' : 'var(--risk-low)', marginTop: '6px', fontWeight: 600 }}>
                {c.flagged_count} flagged ({((c.flagged_count / c.count) * 100).toFixed(1)}%)
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

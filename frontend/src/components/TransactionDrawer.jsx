import React from 'react';
import { X, ExternalLink, RefreshCw, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import RiskBadge from './RiskBadge';

export default function TransactionDrawer({ transaction, onClose, onReassess }) {
  if (!transaction) return null;

  return (
    <div className="drawer">
      <div className="drawer-header">
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Transaction Details</h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {transaction.transaction_reference}
          </span>
        </div>
        <button 
          onClick={onClose} 
          className="button button-secondary button-sm" 
          style={{ padding: '4px' }}
        >
          <X size={18} />
        </button>
      </div>

      <div className="drawer-body">
        {/* Risk Score Summary Banner */}
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          borderRadius: '10px',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              RISK ASSESSMENT ({transaction.rules_version || 'v1.0'})
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
              {transaction.risk_score !== undefined ? `${transaction.risk_score} / 100` : 'Not Assessed'}
            </div>
          </div>
          <RiskBadge score={transaction.risk_score} level={transaction.risk_level} />
        </div>

        {/* Action button */}
        {onReassess && (
          <button 
            onClick={() => onReassess(transaction.id)} 
            className="button button-secondary button-sm"
            style={{ width: '100%', gap: '8px' }}
          >
            <RefreshCw size={14} />
            <span>Re-evaluate Risk Engine Rules</span>
          </button>
        )}

        {/* Transaction Summary Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          backgroundColor: 'var(--bg-card-subtle)',
          padding: '14px',
          borderRadius: '8px',
          fontSize: '0.85rem'
        }}>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Amount</span>
            <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>
              ${Number(transaction.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })} {transaction.currency}
            </strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Status</span>
            <span style={{ textTransform: 'capitalize', fontWeight: 600 }}>{transaction.transaction_status}</span>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Customer</span>
            <strong>{transaction.customer_name}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Merchant</span>
            <strong>{transaction.merchant_name}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Location</span>
            <span>{transaction.location} ({transaction.country_code})</span>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Timestamp</span>
            <span>{new Date(transaction.transaction_timestamp).toLocaleString()}</span>
          </div>
        </div>

        {/* Triggered Risk Factors */}
        <div>
          <h4 style={{ fontSize: '0.92rem', fontWeight: 600, marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertCircle size={16} color="var(--accent-blue)" />
            <span>Triggered Risk Factors ({transaction.factors?.length || 0})</span>
          </h4>

          {(!transaction.factors || transaction.factors.length === 0) ? (
            <div style={{
              padding: '20px',
              textAlign: 'center',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              fontSize: '0.85rem'
            }}>
              <CheckCircle size={24} color="var(--risk-low)" style={{ marginBottom: '6px' }} />
              <div>No fraud heuristics triggered. Baseline low-risk transaction.</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {transaction.factors.map((f, i) => (
                <div key={i} style={{
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '12px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f8fafc' }}>{f.rule_name}</span>
                    <span style={{
                      backgroundColor: 'rgba(239, 68, 68, 0.2)',
                      color: '#f87171',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: 700
                    }}>
                      +{f.points} pts
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-dark)', marginBottom: '4px' }}>
                    {f.rule_code}
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                    {f.explanation}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Case Info if flagged */}
        {transaction.case_id && (
          <div style={{
            padding: '14px',
            backgroundColor: 'rgba(59, 130, 246, 0.08)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            borderRadius: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-blue)' }}>
                Investigation Case #{transaction.case_id}
              </span>
              <span className={`status-badge status-${transaction.case_status}`}>
                {transaction.case_status}
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              This transaction has generated an active investigation case due to elevated risk scoring.
            </p>
          </div>
        )}
      </div>

      <div className="drawer-footer">
        <button onClick={onClose} className="button button-secondary">Close Inspector</button>
      </div>
    </div>
  );
}

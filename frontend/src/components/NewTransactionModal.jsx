import React, { useState, useEffect } from 'react';
import { X, Send, AlertTriangle } from 'lucide-react';
import { adminApi, transactionsApi } from '../api/client';

export default function NewTransactionModal({ onClose, onSuccess }) {
  const [customers, setCustomers] = useState([]);
  const [merchants, setMerchants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [form, setForm] = useState({
    customer_id: '',
    merchant_id: '',
    amount: '120.00',
    currency: 'USD',
    channel: 'online',
    location: 'New York, USA',
    country_code: 'US',
    transaction_status: 'approved'
  });

  useEffect(() => {
    async function loadData() {
      try {
        const [cRes, mRes] = await Promise.all([
          adminApi.getCustomers(),
          adminApi.getMerchants()
        ]);
        setCustomers(cRes.customers || []);
        setMerchants(mRes.merchants || []);
        if (cRes.customers?.length > 0) {
          setForm(prev => ({ ...prev, customer_id: cRes.customers[0].id }));
        }
        if (mRes.merchants?.length > 0) {
          setForm(prev => ({ ...prev, merchant_id: mRes.merchants[0].id }));
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const res = await transactionsApi.createTransaction({
        ...form,
        customer_id: Number(form.customer_id),
        merchant_id: Number(form.merchant_id),
        amount: Number(form.amount)
      });
      if (onSuccess) onSuccess(res);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to submit transaction');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Create Synthetic Transaction</h3>
          <button onClick={onClose} className="button button-secondary button-sm" style={{ padding: '4px' }}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div style={{
                padding: '10px 14px',
                backgroundColor: 'var(--risk-critical-bg)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                borderRadius: '8px',
                color: 'var(--risk-critical)',
                fontSize: '0.85rem'
              }}>
                {error}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Customer
                </label>
                <select 
                  name="customer_id" 
                  value={form.customer_id} 
                  onChange={handleChange} 
                  className="select" 
                  style={{ width: '100%' }}
                  disabled={loading}
                >
                  {customers.map(c => (
                    <option key={c.id} value={c.id}>{c.full_name} ({c.customer_reference})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Merchant
                </label>
                <select 
                  name="merchant_id" 
                  value={form.merchant_id} 
                  onChange={handleChange} 
                  className="select" 
                  style={{ width: '100%' }}
                  disabled={loading}
                >
                  {merchants.map(m => (
                    <option key={m.id} value={m.id}>{m.merchant_name} ({m.category})</option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Amount ($ USD)
                </label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0.01"
                  name="amount" 
                  value={form.amount} 
                  onChange={handleChange} 
                  className="input" 
                  style={{ width: '100%' }}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Status
                </label>
                <select 
                  name="transaction_status" 
                  value={form.transaction_status} 
                  onChange={handleChange} 
                  className="select" 
                  style={{ width: '100%' }}
                >
                  <option value="approved">Approved</option>
                  <option value="declined">Declined</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Channel
                </label>
                <select 
                  name="channel" 
                  value={form.channel} 
                  onChange={handleChange} 
                  className="select" 
                  style={{ width: '100%' }}
                >
                  <option value="online">Online Web</option>
                  <option value="mobile">Mobile App</option>
                  <option value="pos">Point of Sale (POS)</option>
                  <option value="atm">ATM</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Country Code (ISO 2)
                </label>
                <select 
                  name="country_code" 
                  value={form.country_code} 
                  onChange={handleChange} 
                  className="select" 
                  style={{ width: '100%' }}
                >
                  <option value="US">US — United States</option>
                  <option value="SG">SG — Singapore</option>
                  <option value="GB">GB — United Kingdom</option>
                  <option value="CH">CH — Switzerland</option>
                  <option value="NG">NG — Nigeria</option>
                  <option value="JP">JP — Japan</option>
                </select>
              </div>
            </div>

            <div style={{
              padding: '12px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: '8px',
              fontSize: '0.8rem',
              color: 'var(--text-muted)',
              display: 'flex',
              gap: '8px',
              alignItems: 'flex-start'
            }}>
              <AlertTriangle size={16} color="var(--risk-medium)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                Saving will invoke the deterministic rule engine immediately. Amounts ≥ $5,000 or country mismatches will trigger fraud heuristics and open an investigation case.
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" onClick={onClose} className="button button-secondary">Cancel</button>
            <button type="submit" disabled={submitting || loading} className="button button-primary">
              <Send size={15} />
              <span>{submitting ? 'Evaluating...' : 'Create & Score Transaction'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

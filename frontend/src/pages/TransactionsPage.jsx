import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Plus, 
  ChevronLeft, 
  ChevronRight, 
  Eye, 
  RefreshCw,
  SlidersHorizontal
} from 'lucide-react';
import { transactionsApi } from '../api/client';
import RiskBadge from '../components/RiskBadge';
import TransactionDrawer from '../components/TransactionDrawer';
import NewTransactionModal from '../components/NewTransactionModal';
import ScenarioBar from '../components/ScenarioBar';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [riskLevel, setRiskLevel] = useState('');
  const [status, setStatus] = useState('');
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');
  const [sortBy, setSortBy] = useState('transaction_timestamp');
  const [sortDir, setSortDir] = useState('desc');

  // Modals & Drawers
  const [selectedTxn, setSelectedTxn] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchTransactions = async (targetPage = page) => {
    try {
      setLoading(true);
      setError(null);
      const res = await transactionsApi.getTransactions({
        page: targetPage,
        limit: 15,
        search,
        risk_level: riskLevel,
        status,
        min_amount: minAmount,
        max_amount: maxAmount,
        sort_by: sortBy,
        sort_dir: sortDir
      });
      setTransactions(res.items || []);
      setTotal(res.total || 0);
      setPage(res.page || 1);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions(1);
  }, [riskLevel, status, sortBy, sortDir]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchTransactions(1);
  };

  const handleInspect = async (id) => {
    try {
      const res = await transactionsApi.getTransaction(id);
      setSelectedTxn(res.transaction);
    } catch (err) {
      alert(`Failed to load transaction: ${err.message}`);
    }
  };

  return (
    <div className="content-body">
      {/* Top Action Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Transaction Monitoring Engine</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Real-time heuristic evaluation pipeline with explainable risk breakdown.
          </p>
        </div>

        <button 
          onClick={() => setShowCreateModal(true)} 
          className="button button-primary"
        >
          <Plus size={16} />
          <span>New Transaction</span>
        </button>
      </div>

      {/* Scenario Bar */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        padding: '12px 16px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}>
        <ScenarioBar onTriggered={() => fetchTransactions(1)} />
      </div>

      {/* Search and Filters Bar */}
      <div className="panel" style={{ padding: '16px' }}>
        <form onSubmit={handleSearchSubmit} className="filter-bar">
          <div style={{ position: 'relative', flex: '1', minWidth: '220px' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '10px' }} />
            <input 
              type="text" 
              placeholder="Search reference, customer, or merchant..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input" 
              style={{ paddingLeft: '36px', width: '100%' }}
            />
          </div>

          <select 
            value={riskLevel} 
            onChange={(e) => setRiskLevel(e.target.value)} 
            className="select"
          >
            <option value="">All Risk Tiers</option>
            <option value="low">Low (0-29)</option>
            <option value="medium">Medium (30-59)</option>
            <option value="high">High (60-79)</option>
            <option value="critical">Critical (80-100)</option>
          </select>

          <select 
            value={status} 
            onChange={(e) => setStatus(e.target.value)} 
            className="select"
          >
            <option value="">All Statuses</option>
            <option value="approved">Approved</option>
            <option value="declined">Declined</option>
            <option value="pending">Pending</option>
          </select>

          <input 
            type="number" 
            placeholder="Min $" 
            value={minAmount} 
            onChange={(e) => setMinAmount(e.target.value)} 
            className="input" 
            style={{ width: '100px' }}
          />

          <input 
            type="number" 
            placeholder="Max $" 
            value={maxAmount} 
            onChange={(e) => setMaxAmount(e.target.value)} 
            className="input" 
            style={{ width: '100px' }}
          />

          <button type="submit" className="button button-secondary">
            Filter
          </button>

          <button 
            type="button" 
            onClick={() => {
              setSearch('');
              setRiskLevel('');
              setStatus('');
              setMinAmount('');
              setMaxAmount('');
              fetchTransactions(1);
            }} 
            className="button button-secondary"
            title="Reset filters"
          >
            Reset
          </button>
        </form>
      </div>

      {/* Transactions Table */}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Reference</th>
              <th>Customer</th>
              <th>Merchant</th>
              <th>Amount</th>
              <th>Risk Assessment</th>
              <th>Location</th>
              <th>Status</th>
              <th>Timestamp</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  Loading transactions...
                </td>
              </tr>
            ) : transactions.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  No matching transactions found.
                </td>
              </tr>
            ) : (
              transactions.map(t => (
                <tr 
                  key={t.id} 
                  onClick={() => handleInspect(t.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--text-main)', fontSize: '0.82rem' }}>
                    {t.transaction_reference}
                  </td>
                  <td>{t.customer_name}</td>
                  <td>
                    <div>{t.merchant_name}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{t.merchant_category}</div>
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    ${Number(t.amount).toFixed(2)}
                  </td>
                  <td>
                    <RiskBadge score={t.risk_score} level={t.risk_level} />
                  </td>
                  <td>
                    {t.location} ({t.country_code})
                  </td>
                  <td>
                    <span style={{
                      textTransform: 'capitalize',
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      color: t.transaction_status === 'approved' ? 'var(--risk-low)' : t.transaction_status === 'declined' ? 'var(--risk-critical)' : 'var(--risk-medium)'
                    }}>
                      {t.transaction_status}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {new Date(t.transaction_timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <button 
                      onClick={() => handleInspect(t.id)}
                      className="button button-secondary button-sm"
                      style={{ padding: '4px 8px' }}
                    >
                      <Eye size={13} />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="pagination">
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Showing {transactions.length} of {total} records • Page {page} of {totalPages}
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            disabled={page <= 1 || loading} 
            onClick={() => fetchTransactions(page - 1)}
            className="button button-secondary button-sm"
          >
            <ChevronLeft size={16} />
            <span>Previous</span>
          </button>
          <button 
            disabled={page >= totalPages || loading} 
            onClick={() => fetchTransactions(page + 1)}
            className="button button-secondary button-sm"
          >
            <span>Next</span>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Inspector Drawer */}
      <TransactionDrawer 
        transaction={selectedTxn}
        onClose={() => setSelectedTxn(null)}
        onReassess={async (id) => {
          await transactionsApi.reassess(id);
          handleInspect(id);
          fetchTransactions(page);
        }}
      />

      {/* New Transaction Modal */}
      {showCreateModal && (
        <NewTransactionModal 
          onClose={() => setShowCreateModal(false)}
          onSuccess={(res) => {
            fetchTransactions(1);
            if (res.transaction_id) handleInspect(res.transaction_id);
          }}
        />
      )}
    </div>
  );
}

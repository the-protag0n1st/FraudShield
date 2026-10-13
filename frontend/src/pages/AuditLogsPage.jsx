import React, { useState, useEffect } from 'react';
import { History, Search, ChevronLeft, ChevronRight, ShieldAlert, Code } from 'lucide-react';
import { adminApi } from '../api/client';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [action, setAction] = useState('');
  const [selectedDetails, setSelectedDetails] = useState(null);

  const fetchLogs = async (targetPage = page) => {
    try {
      setLoading(true);
      const res = await adminApi.getAuditLogs({
        page: targetPage,
        limit: 20,
        action
      });
      setLogs(res.items || []);
      setTotal(res.total || 0);
      setPage(res.page || 1);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      alert(`Error loading audit logs: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs(1);
  }, [action]);

  return (
    <div className="content-body">
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Immutable System Audit Log</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Security-sensitive actions captured in MySQL InnoDB and protected by database triggers against updates and deletions.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="panel" style={{ padding: '16px' }}>
        <div className="filter-bar">
          <select value={action} onChange={(e) => setAction(e.target.value)} className="select">
            <option value="">All Action Types</option>
            <option value="USER_LOGIN">USER_LOGIN</option>
            <option value="USER_LOGOUT">USER_LOGOUT</option>
            <option value="CASE_STATUS_UPDATED">CASE_STATUS_UPDATED</option>
            <option value="CASE_NOTE_ADDED">CASE_NOTE_ADDED</option>
            <option value="CASE_ASSIGNMENT_UPDATED">CASE_ASSIGNMENT_UPDATED</option>
            <option value="TRANSACTION_ASSESSED">TRANSACTION_ASSESSED</option>
          </select>

          <button onClick={() => fetchLogs(1)} className="button button-secondary">
            Refresh Log
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Actor</th>
              <th>Role</th>
              <th>Action Code</th>
              <th>Target Entity</th>
              <th>Entity ID</th>
              <th>Audit Payload</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  Loading immutable audit records...
                </td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  No audit logs recorded for current criteria.
                </td>
              </tr>
            ) : (
              logs.map(log => (
                <tr key={log.id}>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    {log.user_name || 'System / Automated'}
                  </td>
                  <td>
                    <span style={{ fontSize: '0.75rem', textTransform: 'capitalize', color: 'var(--text-muted)' }}>
                      {log.user_role || 'system'}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      color: 'var(--accent-blue)'
                    }}>
                      {log.action}
                    </span>
                  </td>
                  <td style={{ textTransform: 'capitalize', fontSize: '0.82rem' }}>
                    {log.entity_type}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                    #{log.entity_id}
                  </td>
                  <td>
                    <button 
                      onClick={() => setSelectedDetails(log.details)}
                      className="button button-secondary button-sm"
                      style={{ padding: '3px 8px', fontSize: '0.75rem' }}
                    >
                      <Code size={12} />
                      <span>View JSON</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination">
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Showing {logs.length} of {total} records • Page {page} of {totalPages}
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            disabled={page <= 1 || loading} 
            onClick={() => fetchLogs(page - 1)}
            className="button button-secondary button-sm"
          >
            <ChevronLeft size={16} />
            <span>Previous</span>
          </button>
          <button 
            disabled={page >= totalPages || loading} 
            onClick={() => fetchLogs(page + 1)}
            className="button button-secondary button-sm"
          >
            <span>Next</span>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* JSON Detail Modal */}
      {selectedDetails && (
        <div className="modal-overlay" onClick={() => setSelectedDetails(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '450px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Audit Event Details Payload</h3>
            </div>
            <div className="modal-body">
              <pre style={{
                backgroundColor: 'var(--bg-surface)',
                padding: '16px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontFamily: 'var(--font-mono)',
                overflowX: 'auto',
                border: '1px solid var(--border-color)',
                color: '#38bdf8'
              }}>
                {typeof selectedDetails === 'string' 
                  ? selectedDetails 
                  : JSON.stringify(selectedDetails, null, 2)}
              </pre>
            </div>
            <div className="modal-footer">
              <button onClick={() => setSelectedDetails(null)} className="button button-secondary">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

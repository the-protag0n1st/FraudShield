import React, { useState, useEffect } from 'react';
import { 
  Briefcase, 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  CheckCircle2, 
  XCircle, 
  MessageSquare, 
  User, 
  Clock, 
  AlertTriangle,
  History,
  X
} from 'lucide-react';
import { casesApi, adminApi } from '../api/client';
import RiskBadge from '../components/RiskBadge';

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [search, setSearch] = useState('');

  const [selectedCase, setSelectedCase] = useState(null);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [usersList, setUsersList] = useState([]);

  // Note form state
  const [newNote, setNewNote] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);

  // Status transition state
  const [statusAction, setStatusAction] = useState('');
  const [resolutionNote, setResolutionNote] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  const fetchCases = async (targetPage = page) => {
    try {
      setLoading(true);
      const res = await casesApi.getCases({
        page: targetPage,
        limit: 15,
        status,
        priority,
        search
      });
      setCases(res.items || []);
      setTotal(res.total || 0);
      setPage(res.page || 1);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      alert(`Error loading cases: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases(1);
    adminApi.getUsers().then(res => setUsersList(res.users || [])).catch(() => {});
  }, [status, priority]);

  const openCaseDetails = async (caseId) => {
    try {
      setDrawerLoading(true);
      const res = await casesApi.getCase(caseId);
      setSelectedCase(res.case);
      setStatusAction(res.case.case_status);
      setResolutionNote(res.case.resolution_notes || '');
    } catch (err) {
      alert(`Failed to load case: ${err.message}`);
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim() || !selectedCase) return;

    try {
      setSubmittingNote(true);
      await casesApi.addNote(selectedCase.case_id, newNote);
      setNewNote('');
      openCaseDetails(selectedCase.case_id);
      fetchCases(page);
    } catch (err) {
      alert(`Failed to add note: ${err.message}`);
    } finally {
      setSubmittingNote(false);
    }
  };

  const handleStatusUpdate = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;

    try {
      setUpdatingStatus(true);
      await casesApi.updateCase(selectedCase.case_id, {
        case_status: statusAction,
        resolution_notes: resolutionNote
      });
      openCaseDetails(selectedCase.case_id);
      fetchCases(page);
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleAssignChange = async (userId) => {
    if (!selectedCase) return;
    try {
      await casesApi.updateCase(selectedCase.case_id, {
        assigned_to: userId ? Number(userId) : null
      });
      openCaseDetails(selectedCase.case_id);
      fetchCases(page);
    } catch (err) {
      alert(`Reassignment failed: ${err.message}`);
    }
  };

  return (
    <div className="content-body">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Investigation Case Management</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Track, assign, review evidence, and execute atomic resolution procedures.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="panel" style={{ padding: '16px' }}>
        <div className="filter-bar">
          <div style={{ position: 'relative', flex: '1', minWidth: '220px' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '10px' }} />
            <input 
              type="text" 
              placeholder="Search reference, customer, or merchant..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchCases(1)}
              className="input" 
              style={{ paddingLeft: '36px', width: '100%' }}
            />
          </div>

          <select value={status} onChange={(e) => setStatus(e.target.value)} className="select">
            <option value="">All Case Statuses</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="resolved_fraud">Resolved Fraud</option>
            <option value="resolved_legitimate">Resolved Legitimate</option>
          </select>

          <select value={priority} onChange={(e) => setPriority(e.target.value)} className="select">
            <option value="">All Priorities</option>
            <option value="critical">Critical Priority</option>
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </select>

          <button onClick={() => fetchCases(1)} className="button button-secondary">
            Filter
          </button>
        </div>
      </div>

      {/* Cases Table */}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Transaction Ref</th>
              <th>Customer</th>
              <th>Merchant</th>
              <th>Amount</th>
              <th>Risk Score</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Assigned Analyst</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="10" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  Loading investigation cases...
                </td>
              </tr>
            ) : cases.length === 0 ? (
              <tr>
                <td colSpan="10" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  No investigation cases matching current filters.
                </td>
              </tr>
            ) : (
              cases.map(c => (
                <tr 
                  key={c.case_id}
                  onClick={() => openCaseDetails(c.case_id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--accent-blue)' }}>
                    #{c.case_id}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                    {c.transaction_reference}
                  </td>
                  <td>{c.customer_name}</td>
                  <td>{c.merchant_name}</td>
                  <td style={{ fontWeight: 600 }}>${Number(c.amount).toFixed(2)}</td>
                  <td>
                    <RiskBadge score={c.risk_score} level={c.risk_level} />
                  </td>
                  <td>
                    <span style={{
                      textTransform: 'uppercase',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: c.priority === 'critical' ? 'var(--risk-critical)' : 'var(--risk-high)'
                    }}>
                      {c.priority}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge status-${c.case_status}`}>
                      {c.case_status}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.85rem', color: c.assigned_to_name ? 'var(--text-main)' : 'var(--text-dark)' }}>
                      {c.assigned_to_name || 'Unassigned'}
                    </span>
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <button 
                      onClick={() => openCaseDetails(c.case_id)}
                      className="button button-secondary button-sm"
                    >
                      Manage
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
          Showing {cases.length} of {total} cases • Page {page} of {totalPages}
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            disabled={page <= 1 || loading} 
            onClick={() => fetchCases(page - 1)}
            className="button button-secondary button-sm"
          >
            <ChevronLeft size={16} />
            <span>Previous</span>
          </button>
          <button 
            disabled={page >= totalPages || loading} 
            onClick={() => fetchCases(page + 1)}
            className="button button-secondary button-sm"
          >
            <span>Next</span>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Case Investigation Drawer */}
      {selectedCase && (
        <div className="drawer" style={{ width: '580px' }}>
          <div className="drawer-header">
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
                Case #{selectedCase.case_id} Investigation
              </h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {selectedCase.transaction_reference} • Created {new Date(selectedCase.case_created_at).toLocaleDateString()}
              </span>
            </div>
            <button onClick={() => setSelectedCase(null)} className="button button-secondary button-sm" style={{ padding: '4px' }}>
              <X size={18} />
            </button>
          </div>

          <div className="drawer-body">
            {/* Quick Overview Cards */}
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
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Transaction Amount</span>
                <strong style={{ fontSize: '1.1rem' }}>
                  ${Number(selectedCase.amount).toFixed(2)} {selectedCase.currency}
                </strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Risk Score</span>
                <RiskBadge score={selectedCase.risk_score} level={selectedCase.risk_level} />
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Customer Profile</span>
                <div>{selectedCase.customer_name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{selectedCase.customer_email}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Merchant</span>
                <div>{selectedCase.merchant_name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{selectedCase.merchant_category}</div>
              </div>
            </div>

            {/* Assignment & Priority */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Assignee
                </label>
                <select 
                  value={selectedCase.assigned_to || ''} 
                  onChange={(e) => handleAssignChange(e.target.value)}
                  className="select"
                  style={{ width: '100%' }}
                >
                  <option value="">Unassigned</option>
                  {usersList.map(u => (
                    <option key={u.id} value={u.id}>{u.full_name} ({u.role})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Current Status
                </label>
                <div style={{ paddingTop: '6px' }}>
                  <span className={`status-badge status-${selectedCase.case_status}`}>
                    {selectedCase.case_status}
                  </span>
                </div>
              </div>
            </div>

            {/* Triggered Evidence Factors */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Triggered Risk Evidence</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {selectedCase.factors?.map((f, i) => (
                  <div key={i} style={{
                    padding: '10px 12px',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{f.rule_name}</span>
                      <span style={{ color: 'var(--risk-critical)', fontWeight: 700, fontSize: '0.8rem' }}>+{f.points} pts</span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{f.explanation}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Resolution Workflow Form */}
            <form onSubmit={handleStatusUpdate} style={{
              padding: '16px',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-light)',
              borderRadius: '8px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                <CheckCircle2 size={16} color="var(--accent-blue)" />
                <span>Execute Case Resolution (Stored Procedure)</span>
              </h4>

              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Target Lifecycle State
                </label>
                <select 
                  value={statusAction} 
                  onChange={(e) => setStatusAction(e.target.value)} 
                  className="select"
                  style={{ width: '100%' }}
                >
                  <option value="open">Open</option>
                  <option value="investigating">Investigating</option>
                  <option value="resolved_fraud">Resolved: Confirmed Fraud</option>
                  <option value="resolved_legitimate">Resolved: Verified Legitimate</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Resolution Notes / Rationale
                </label>
                <textarea 
                  value={resolutionNote} 
                  onChange={(e) => setResolutionNote(e.target.value)}
                  placeholder="Record verification details, issuer confirmation, or chargeback outcome..."
                  className="textarea"
                  style={{ width: '100%', minHeight: '60px' }}
                />
              </div>

              <button 
                type="submit" 
                disabled={updatingStatus}
                className="button button-primary button-sm"
                style={{ alignSelf: 'flex-end' }}
              >
                {updatingStatus ? 'Updating via Stored Procedure...' : 'Save Lifecycle Status'}
              </button>
            </form>

            {/* Analyst Notes Thread */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MessageSquare size={16} color="var(--accent-cyan)" />
                <span>Analyst Investigation Notes ({selectedCase.notes?.length || 0})</span>
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '12px' }}>
                {selectedCase.notes?.map(n => (
                  <div key={n.id} style={{
                    padding: '10px 12px',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '0.78rem' }}>
                      <strong style={{ color: 'var(--accent-blue)' }}>{n.author_name} ({n.author_role})</strong>
                      <span style={{ color: 'var(--text-muted)' }}>{new Date(n.created_at).toLocaleString()}</span>
                    </div>
                    <p style={{ fontSize: '0.83rem', color: 'var(--text-main)', lineHeight: '1.4' }}>{n.note_text}</p>
                  </div>
                ))}
              </div>

              {/* Add Note Input */}
              <form onSubmit={handleAddNote} style={{ display: 'flex', gap: '8px' }}>
                <input 
                  type="text"
                  placeholder="Add case observation..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="input"
                  style={{ flex: 1 }}
                />
                <button type="submit" disabled={submittingNote || !newNote.trim()} className="button button-secondary">
                  Add Note
                </button>
              </form>
            </div>

            {/* Case Audit History */}
            {selectedCase.audit_history?.length > 0 && (
              <div>
                <h4 style={{ fontSize: '0.88rem', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <History size={15} color="var(--text-muted)" />
                  <span>Audit Trail</span>
                </h4>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {selectedCase.audit_history.map(a => (
                    <div key={a.id} style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '4px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{a.action}</span> by {a.actor_name || 'System'} at {new Date(a.created_at).toLocaleString()}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="drawer-footer">
            <button onClick={() => setSelectedCase(null)} className="button button-secondary">Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

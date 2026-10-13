import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Shield, 
  LayoutDashboard, 
  ArrowLeftRight, 
  Briefcase, 
  BarChart3, 
  History, 
  LogOut,
  UserCheck
} from 'lucide-react';

export default function Sidebar({ user, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Shield size={22} />
        </div>
        <div>
          <h1 className="sidebar-title">FraudShield</h1>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink 
          to="/" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} />
          <span>Overview</span>
        </NavLink>

        <NavLink 
          to="/transactions" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <ArrowLeftRight size={18} />
          <span>Transactions</span>
        </NavLink>

        <NavLink 
          to="/cases" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Briefcase size={18} />
          <span>Investigations</span>
        </NavLink>

        <NavLink 
          to="/analytics" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <BarChart3 size={18} />
          <span>Analytics</span>
        </NavLink>

        <NavLink 
          to="/audit-logs" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <History size={18} />
          <span>Audit Logs</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="user-info">
            <span className="user-name">{user?.full_name || 'Active User'}</span>
            <span className="user-role-badge">{user?.role || 'investigator'}</span>
          </div>
          <button 
            onClick={onLogout} 
            className="button button-secondary button-sm"
            title="Log out"
            style={{ padding: '6px' }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}

import React, { useState } from 'react';
import { Shield, Lock, Mail, ArrowRight, ShieldCheck, UserCheck } from 'lucide-react';
import { authApi } from '../api/client';

export default function LoginPage({ onLoginSuccess }) {
  const [email, setEmail] = useState('admin@fraudshield.local');
  const [password, setPassword] = useState('Admin@123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await authApi.login(email, password);
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'var(--bg-main)',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '420px',
        backgroundColor: 'var(--bg-card)',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        padding: '36px 32px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '48px',
            height: '48px',
            background: 'linear-gradient(135deg, #3b82f6, #06b6d4)',
            borderRadius: '12px',
            color: 'white',
            marginBottom: '16px',
            boxShadow: '0 8px 16px rgba(59, 130, 246, 0.3)'
          }}>
            <Shield size={26} />
          </div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '4px' }}>
            FraudShield
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Financial Transaction Risk & Heuristic Engine
          </p>
        </div>

        {error && (
          <div style={{
            padding: '10px 14px',
            backgroundColor: 'var(--risk-critical-bg)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '8px',
            color: 'var(--risk-critical)',
            fontSize: '0.85rem',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '11px' }} />
              <input 
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@fraudshield.local"
                className="input"
                style={{ width: '100%', paddingLeft: '36px' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '11px' }} />
              <input 
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="input"
                style={{ width: '100%', paddingLeft: '36px' }}
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="button button-primary"
            style={{ width: '100%', padding: '10px', marginTop: '4px' }}
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Console'}</span>
            <ArrowRight size={16} />
          </button>
        </form>

        {/* Demo Credentials Quick-Fill */}
        <div style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em', textAlign: 'center', marginBottom: '12px' }}>
            Quick Demo Accounts
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <button
              type="button"
              onClick={() => fillCredentials('admin@fraudshield.local', 'Admin@123')}
              className="button button-secondary button-sm"
              style={{ fontSize: '0.78rem' }}
            >
              <ShieldCheck size={14} color="var(--accent-blue)" />
              <span>Admin</span>
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('investigator@fraudshield.local', 'Investigator@123')}
              className="button button-secondary button-sm"
              style={{ fontSize: '0.78rem' }}
            >
              <UserCheck size={14} color="var(--accent-cyan)" />
              <span>Analyst</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

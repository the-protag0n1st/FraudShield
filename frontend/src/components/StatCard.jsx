import React from 'react';

export default function StatCard({ title, value, subtext, icon: Icon, alert }) {
  return (
    <div className={`stat-card ${alert ? 'alert' : ''}`}>
      <div className="stat-header">
        <span>{title}</span>
        {Icon && <Icon size={18} style={{ opacity: 0.8 }} />}
      </div>
      <div className="stat-value">{value}</div>
      {subtext && <div className="stat-subtext">{subtext}</div>}
    </div>
  );
}

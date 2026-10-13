import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function RiskBadge({ score, level }) {
  const lvl = (level || 'low').toLowerCase();

  const icons = {
    critical: <ShieldAlert size={14} />,
    high: <ShieldAlert size={14} />,
    medium: <AlertTriangle size={14} />,
    low: <ShieldCheck size={14} />
  };

  return (
    <span className={`badge badge-${lvl}`}>
      {icons[lvl]}
      <span>{score !== undefined ? `${score} pts • ` : ''}{lvl}</span>
    </span>
  );
}

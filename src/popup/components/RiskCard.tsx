import React from 'react';
import { ShieldAlert, ShieldCheck, Globe, Calendar } from 'lucide-react';
import { ScanResult } from '../../shared/types';

interface RiskCardProps {
  result: ScanResult;
}

export const RiskCard: React.FC<RiskCardProps> = ({ result }) => {
  const { title, url, label, timestamp } = result;

  const getBadgeConfig = (riskLabel: typeof label) => {
    switch (riskLabel) {
      case 'Risky':
        return {
          color: 'var(--risky)',
          bgColor: 'rgba(239, 68, 68, 0.12)',
          icon: <ShieldAlert size={14} color="var(--risky)" />,
          description: 'High risk elements detected. Proceed with warning.'
        };
      case 'Caution':
        return {
          color: 'var(--caution)',
          bgColor: 'rgba(245, 158, 11, 0.12)',
          icon: <ShieldAlert size={14} color="var(--caution)" />,
          description: 'Suspicious tactics found. Verify claims before acting.'
        };
      case 'Safe':
      default:
        return {
          color: 'var(--safe)',
          bgColor: 'rgba(16, 185, 129, 0.12)',
          icon: <ShieldCheck size={14} color="var(--safe)" />,
          description: 'Low-risk profile. Safe from manipulation patterns.'
        };
    }
  };

  const config = getBadgeConfig(label);

  return (
    <div className="card risk-card">
      <h2 className="page-title" title={title}>
        {title || 'Untitled Page'}
      </h2>

      <div className="url-row" title={url}>
        <Globe size={12} className="url-icon" />
        <span className="page-url">{url || 'Unknown website'}</span>
      </div>

      <div className="badge-row">
        <span
          className="risk-badge"
          style={{
            backgroundColor: config.bgColor,
            color: config.color,
            borderColor: `${config.color}33`,
          }}
        >
          {config.icon}
          <span className="risk-badge-text">{label}</span>
        </span>

        <div className="timestamp-row">
          <Calendar size={11} className="time-icon" />
          <span>{timestamp}</span>
        </div>
      </div>

      <p className="risk-description">{config.description}</p>
    </div>
  );
};

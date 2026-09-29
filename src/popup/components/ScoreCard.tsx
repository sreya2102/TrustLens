import React from 'react';
import { FileText, Type, MousePointer, Link } from 'lucide-react';
import { ScanResult } from '../../shared/types';

interface ScoreCardProps {
  result: ScanResult;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ result }) => {
  const { score, wordCount, headingCount, buttonCount, linkCount } = result;

  // Determine indicator color based on threat level
  const getScoreColor = (val: number) => {
    if (val > 50) return 'var(--risky)';
    if (val > 20) return 'var(--caution)';
    return 'var(--safe)';
  };

  const scoreColor = getScoreColor(score);

  // SVG Circular progress configurations
  const radius = 32;
  const strokeWidth = 5;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="card score-card">
      <div className="circular-container">
        <svg width="90" height="90" viewBox="0 0 90 90" className="circular-chart">
          {/* Background circle */}
          <circle
            className="circle-bg"
            cx="45"
            cy="45"
            r={radius}
            fill="transparent"
            stroke="var(--border)"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            className="circle-progress"
            cx="45"
            cy="45"
            r={radius}
            fill="transparent"
            stroke={scoreColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform="rotate(-90 45 45)"
          />
          {/* Score text */}
          <text
            x="45"
            y="49"
            className="circle-score-text"
            textAnchor="middle"
            fill="var(--text-light)"
            fontWeight="bold"
            fontSize="18"
          >
            {score}
          </text>
          <text
            x="45"
            y="62"
            className="circle-score-total"
            textAnchor="middle"
            fill="var(--text-muted)"
            fontSize="8"
          >
            / 100
          </text>
        </svg>
        <div className="circular-info">
          <div className="circular-title">Manipulative Score</div>
          <div className="circular-desc" style={{ color: scoreColor }}>
            {score > 50 ? 'High Risk' : score > 20 ? 'Moderate Alert' : 'Minimal Pattern'}
          </div>
        </div>
      </div>

      <div className="stats-divider" />

      <div className="stats-grid">
        <div className="stat-item" title="Word count">
          <div className="stat-icon-wrapper">
            <FileText size={14} className="stat-icon" />
          </div>
          <div className="stat-details">
            <span className="stat-value">{wordCount}</span>
            <span className="stat-label">Words</span>
          </div>
        </div>

        <div className="stat-item" title="Heading elements">
          <div className="stat-icon-wrapper">
            <Type size={14} className="stat-icon" />
          </div>
          <div className="stat-details">
            <span className="stat-value">{headingCount}</span>
            <span className="stat-label">Headings</span>
          </div>
        </div>

        <div className="stat-item" title="Interactive button elements">
          <div className="stat-icon-wrapper">
            <MousePointer size={14} className="stat-icon" />
          </div>
          <div className="stat-details">
            <span className="stat-value">{buttonCount}</span>
            <span className="stat-label">Buttons</span>
          </div>
        </div>

        <div className="stat-item" title="Hyperlink elements">
          <div className="stat-icon-wrapper">
            <Link size={14} className="stat-icon" />
          </div>
          <div className="stat-details">
            <span className="stat-value">{linkCount}</span>
            <span className="stat-label">Links</span>
          </div>
        </div>
      </div>
    </div>
  );
};

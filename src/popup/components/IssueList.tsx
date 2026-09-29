import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

interface IssueListProps {
  reasons: string[];
}

export const IssueList: React.FC<IssueListProps> = ({ reasons }) => {
  const hasIssues = reasons && reasons.length > 0;

  return (
    <div className="card issues-card">
      <h3 className="card-section-title">Detected Issues</h3>
      {hasIssues ? (
        <ul className="issues-list">
          {reasons.map((reason, index) => {
            // Strip the ⚠ character from the reason text, as we use Lucide icons
            const cleanReason = reason.replace(/^⚠\s*/, '');
            return (
              <li key={index} className="issue-item">
                <AlertTriangle size={13} className="issue-icon" />
                <span className="issue-text">{cleanReason}</span>
              </li>
            );
          })}
        </ul>
      ) : (
        <div className="no-issues">
          <ShieldCheck size={16} className="no-issues-icon" />
          <span>No manipulation patterns or dark patterns detected.</span>
        </div>
      )}
    </div>
  );
};

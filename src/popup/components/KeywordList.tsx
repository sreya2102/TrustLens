import React from 'react';
import { KeywordMatch } from '../../shared/types';

interface KeywordListProps {
  matchedKeywords: KeywordMatch[];
}

export const KeywordList: React.FC<KeywordListProps> = ({ matchedKeywords }) => {
  const hasKeywords = matchedKeywords && matchedKeywords.length > 0;

  // Sort keywords by weight descending to list higher threats first
  const sortedKeywords = [...matchedKeywords].sort((a, b) => b.weight - a.weight);

  const formatCategory = (cat: string) => {
    return cat.replace('_', ' ');
  };

  return (
    <div className="card keywords-card">
      <h3 className="card-section-title">Matched Keywords</h3>
      {hasKeywords ? (
        <div className="keywords-badge-container">
          {sortedKeywords.map((match, index) => (
            <div
              key={index}
              className="keyword-tag"
              style={{
                backgroundColor: `${match.color}1e`,
                color: match.color,
                borderColor: `${match.color}40`,
              }}
              title={`Category: ${formatCategory(match.category)} | Weight: +${match.weight * match.count}`}
            >
              <span className="keyword-name">{match.keyword}</span>
              <span
                className="keyword-badge-count"
                style={{
                  backgroundColor: match.color,
                  color: '#0f172a',
                }}
              >
                {match.count}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-keywords">
          <span>No suspicious key phrases found.</span>
        </div>
      )}
    </div>
  );
};

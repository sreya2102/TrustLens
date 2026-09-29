import React from 'react';
import { Cpu, ShieldAlert, Calendar, Database, CheckCircle, Percent, Activity } from 'lucide-react';
import { ScanResult } from '../../shared/types';
import modelInfo from '../../ml/modelInfo.json';

interface MLCardProps {
  result: ScanResult;
}

export const MLCard: React.FC<MLCardProps> = ({ result }) => {
  const { 
    ruleScore = 0, 
    mlScore = 0, 
    score = 0, 
    mlPrediction = 'Safe', 
    mlConfidence = 0.0,
    modelName = modelInfo.modelName,
    modelVersion = `v${modelInfo.version}`,
    modelAccuracy = modelInfo.accuracy,
    modelLatency,
    modelMemory
  } = result;

  // Formatting confidence
  const confidencePct = Math.round(mlConfidence * 100);

  // Class badge color based on prediction
  const getBadgeStyle = (label: string) => {
    switch (label) {
      case 'Risky':
        return {
          backgroundColor: 'rgba(239, 68, 68, 0.12)',
          color: 'var(--risky)',
          borderColor: 'var(--risky)'
        };
      case 'Caution':
        return {
          backgroundColor: 'rgba(245, 158, 11, 0.12)',
          color: 'var(--caution)',
          borderColor: 'var(--caution)'
        };
      case 'Safe':
      default:
        return {
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          color: 'var(--safe)',
          borderColor: 'var(--safe)'
        };
    }
  };

  const badgeStyle = getBadgeStyle(mlPrediction);

  return (
    <div className="card ml-card">
      <div className="ml-card-header">
        <Cpu size={16} className="ml-header-icon" />
        <h3 className="card-section-title ml-title">AI Decision Engine</h3>
        <span 
          className="ml-verdict-badge"
          style={{
            backgroundColor: badgeStyle.backgroundColor,
            color: badgeStyle.color,
            borderColor: `${badgeStyle.color}40`,
            borderWidth: '1px',
            borderStyle: 'solid'
          }}
        >
          {mlPrediction} ({confidencePct}%)
        </span>
      </div>

      {/* Progress Bars for Scoring Breakdown */}
      <div className="score-breakdown">
        <div className="score-row">
          <div className="score-labels">
            <span className="score-name">Rule Engine (60% weight)</span>
            <span className="score-value">{ruleScore}/100</span>
          </div>
          <div className="progress-bar-bg">
            <div 
              className="progress-bar-fill rule-fill" 
              style={{ width: `${ruleScore}%` }}
            />
          </div>
        </div>

        <div className="score-row">
          <div className="score-labels">
            <span className="score-name">ML Predictor (40% weight)</span>
            <span className="score-value">{mlScore}/100</span>
          </div>
          <div className="progress-bar-bg">
            <div 
              className="progress-bar-fill ml-fill" 
              style={{ width: `${mlScore}%` }}
            />
          </div>
        </div>

        <div className="score-row combined-row">
          <div className="score-labels">
            <span className="score-name combined-name">Hybrid Combined Score</span>
            <span className="score-value combined-val">{score}/100</span>
          </div>
          <div className="progress-bar-bg">
            <div 
              className="progress-bar-fill combined-fill" 
              style={{ 
                width: `${score}%`,
                backgroundColor: score > 50 ? 'var(--risky)' : score > 20 ? 'var(--caution)' : 'var(--safe)'
              }}
            />
          </div>
        </div>
      </div>

      {/* Accordion/Grid for Model Metadata */}
      <div className="model-meta-grid">
        <div className="meta-item" title="Model Architecture">
          <Cpu size={12} className="meta-icon" />
          <span className="meta-lbl">Model:</span>
          <span className="meta-val">{modelName}</span>
        </div>
        <div className="meta-item" title="Model Version">
          <ShieldAlert size={12} className="meta-icon" />
          <span className="meta-lbl">Version:</span>
          <span className="meta-val">{modelVersion.startsWith('v') ? modelVersion : `v${modelVersion}`}</span>
        </div>
        <div className="meta-item" title="Dataset Size used for training">
          <Database size={12} className="meta-icon" />
          <span className="meta-lbl">Dataset:</span>
          <span className="meta-val">{modelInfo.datasetSize} pages</span>
        </div>
        <div className="meta-item" title="Training Date">
          <Calendar size={12} className="meta-icon" />
          <span className="meta-lbl">Trained:</span>
          <span className="meta-val">{modelInfo.trainingDate}</span>
        </div>
        <div className="meta-item" title="Test Accuracy">
          <CheckCircle size={12} className="meta-icon" />
          <span className="meta-lbl">Accuracy:</span>
          <span className="meta-val">{(modelAccuracy > 1.0 ? modelAccuracy : modelAccuracy * 100).toFixed(1)}%</span>
        </div>
        
        {modelLatency !== undefined ? (
          <div className="meta-item" title="Model Latency">
            <Activity size={12} className="meta-icon" style={{ color: 'var(--caution)' }} />
            <span className="meta-lbl">Latency:</span>
            <span className="meta-val">{modelLatency} ms</span>
          </div>
        ) : (
          <div className="meta-item" title="Test F1-score">
            <Percent size={12} className="meta-icon" />
            <span className="meta-lbl">F1 Score:</span>
            <span className="meta-val">{(modelInfo.f1 * 100).toFixed(1)}%</span>
          </div>
        )}

        {modelMemory !== undefined && (
          <div className="meta-item" title="Model Memory RSS usage">
            <Database size={12} className="meta-icon" style={{ color: 'var(--primary)' }} />
            <span className="meta-lbl">RAM usage:</span>
            <span className="meta-val">{modelMemory} MB</span>
          </div>
        )}
      </div>
    </div>
  );
};

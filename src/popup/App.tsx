import { useState, useEffect } from 'react';
import { 
  Shield, 
  Scan, 
  Loader2, 
  AlertCircle, 
  Settings, 
  ThumbsUp, 
  ThumbsDown, 
  Check, 
  Info, 
  Lock, 
  Unlock, 
  Calendar, 
  Globe, 
  Eye 
} from 'lucide-react';
import { ScanResult } from '../shared/types';
import { UI_MESSAGES } from '../shared/constants';
import { ScoreCard } from './components/ScoreCard';
import { RiskCard } from './components/RiskCard';
import { MLCard } from './components/MLCard';
import { IssueList } from './components/IssueList';
import { KeywordList } from './components/KeywordList';
import modelInfo from '../ml/modelInfo.json';

// Helper to compare semver versions
function isNewerVersion(local: string, remote: string): boolean {
  const l = local.split('.').map(Number);
  const r = remote.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    if (r[i] > (l[i] || 0)) return true;
    if (r[i] < (l[i] || 0)) return false;
  }
  return false;
}

function App() {
  const [status, setStatus] = useState<string>(UI_MESSAGES.READY);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Settings State
  const [mode, setMode] = useState<'local' | 'cloud' | 'hybrid'>('local');
  const [backendUrl, setBackendUrl] = useState<string>('http://localhost:8000');
  const [autoScanEnabled, setAutoScanEnabled] = useState<boolean>(false);
  const [activeModel, setActiveModel] = useState<string>('logistic_regression');
  
  const [showSettings, setShowSettings] = useState(false);
  const [userId, setUserId] = useState<string>('');
  const [newModelVersion, setNewModelVersion] = useState<string | null>(null);

  // Tab View for scan results: 'risk' (threat scanner) or 'reputation' (reputation & privacy summarizer)
  const [activeTab, setActiveTab] = useState<'risk' | 'reputation'>('risk');

  // User Feedback state
  const [feedbackRating, setFeedbackRating] = useState<'correct' | 'wrong' | null>(null);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackStatus, setFeedbackStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');

  // Load settings on startup
  useEffect(() => {
    // 1. Load extension configuration
    chrome.storage.local.get(['trustlens_settings'], (store) => {
      if (store.trustlens_settings) {
        setMode(store.trustlens_settings.mode || 'local');
        setBackendUrl(store.trustlens_settings.backendUrl || 'http://localhost:8000');
        setAutoScanEnabled(store.trustlens_settings.autoScanEnabled || false);
        setActiveModel(store.trustlens_settings.activeModel || 'logistic_regression');
      }
    });

    // 2. Silent guest user identification
    chrome.storage.local.get(['trustlens_user_id'], (store) => {
      if (store.trustlens_user_id) {
        setUserId(store.trustlens_user_id);
      } else {
        const newId = crypto.randomUUID();
        chrome.storage.local.set({ trustlens_user_id: newId });
        setUserId(newId);
      }
    });

    // 3. Attempt to load cached scan for active tab URL instantly (Performance optimization)
    checkScanCache();
  }, []);

  // Check remote model version
  useEffect(() => {
    if (backendUrl) {
      fetch(`${backendUrl}/api/model`)
        .then((res) => {
          if (!res.ok) throw new Error();
          return res.json();
        })
        .then((data) => {
          if (data && data.version) {
            const localVersion = modelInfo.version;
            if (isNewerVersion(localVersion, data.version)) {
              setNewModelVersion(data.version);
            } else {
              setNewModelVersion(null);
            }
          }
        })
        .catch(() => {
          setNewModelVersion(null);
        });
    }
  }, [backendUrl, mode]);

  const checkScanCache = async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.url) return;
      
      const currentUrl = tab.url;
      chrome.storage.local.get(['trustlens_scan_cache'], (store) => {
        const cache = store.trustlens_scan_cache || {};
        const cachedItem = cache[currentUrl];
        
        if (cachedItem) {
          const age = Date.now() - cachedItem.cachedAt;
          const maxAge = 30 * 60 * 1000; // 30 minutes cache duration
          
          if (age < maxAge) {
            console.log(`Restoring scan results from local cache for URL: ${currentUrl}`);
            setResult(cachedItem.data);
          }
        }
      });
    } catch (e) {
      console.warn('Cache lookup failed:', e);
    }
  };

  const saveSettings = (newMode: 'local' | 'cloud' | 'hybrid', newUrl: string, newAuto: boolean, newModel: string) => {
    setMode(newMode);
    setBackendUrl(newUrl);
    setAutoScanEnabled(newAuto);
    setActiveModel(newModel);
    chrome.storage.local.set({
      trustlens_settings: { 
        mode: newMode, 
        backendUrl: newUrl, 
        autoScanEnabled: newAuto, 
        activeModel: newModel 
      }
    });
  };

  const handleScan = async (bypassCache = false) => {
    setIsScanning(true);
    setStatus(UI_MESSAGES.SCANNING);
    setErrorMessage(null);
    setFeedbackRating(null);
    setFeedbackComment('');
    setFeedbackStatus('idle');

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) {
        throw new Error('No active tab found. Please open a webpage.');
      }

      const url = tab.url || '';
      if (
        url.startsWith('chrome://') || 
        url.startsWith('chrome-extension://') || 
        url.startsWith('https://chrome.google.com/webstore') ||
        url.startsWith('about:')
      ) {
        throw new Error('TrustLens cannot scan browser system pages. Please try on a standard website.');
      }

      // Check performance cache first (bypass if clicked 'Rescan')
      if (!bypassCache) {
        let isCached = false;
        const cachePromise = new Promise<ScanResult | null>((resolve) => {
          chrome.storage.local.get(['trustlens_scan_cache'], (store) => {
            const cache = store.trustlens_scan_cache || {};
            const cachedItem = cache[url];
            if (cachedItem && (Date.now() - cachedItem.cachedAt < 30 * 60 * 1000)) {
              isCached = true;
              resolve(cachedItem.data);
            } else {
              resolve(null);
            }
          });
        });
        const cachedRes = await cachePromise;
        if (isCached && cachedRes) {
          setResult(cachedRes);
          setStatus(UI_MESSAGES.READY);
          setIsScanning(false);
          return;
        }
      }

      // Extract DOM content via Content Script
      let response;
      try {
        response = await chrome.tabs.sendMessage(tab.id, { type: 'SCAN_PAGE' });
      } catch (err) {
        console.warn('Direct messaging failed, attempting injection...', err);
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content.js']
        });
        response = await chrome.tabs.sendMessage(tab.id, { type: 'SCAN_PAGE' });
      }
      
      if (!response || !response.success) {
        const errText = response?.error || 'Content script failed to extract data.';
        throw new Error(errText);
      }

      const localResult = response.data as ScanResult;
      const extractedData = response.extractedData;

      let finalResult: ScanResult = localResult;
      let cloudResult: ScanResult | null = null;

      // Cloud/Hybrid analysis execution
      if (mode === 'cloud' || mode === 'hybrid') {
        try {
          const apiRes = await fetch(`${backendUrl}/api/scan`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              pageText: extractedData.visibleText,
              url: extractedData.url,
              title: extractedData.title,
              userId: userId,
              activeModel: activeModel
            })
          });

          if (!apiRes.ok) {
            throw new Error(`Server returned status: ${apiRes.status}`);
          }

          const cloudData = await apiRes.json();
          cloudResult = {
            title: cloudData.title,
            url: cloudData.url,
            wordCount: extractedData.wordCount,
            headingCount: extractedData.headingCount,
            buttonCount: extractedData.buttonCount,
            linkCount: extractedData.linkCount,
            score: cloudData.score,
            label: cloudData.label,
            matchedKeywords: cloudData.matchedKeywords,
            reasons: cloudData.reasons,
            timestamp: cloudData.timestamp,
            ruleScore: cloudData.ruleScore,
            mlScore: cloudData.mlScore,
            mlPrediction: cloudData.mlPrediction,
            mlConfidence: cloudData.mlConfidence,
            scanId: cloudData.scanId,
            modelName: cloudData.modelName,
            modelVersion: cloudData.modelVersion,
            modelAccuracy: cloudData.modelAccuracy,
            modelLatency: cloudData.modelLatency,
            modelMemory: cloudData.modelMemory,
            humanExplanation: cloudData.humanExplanation,
            influentialWords: cloudData.influentialWords,
            isPrivacyPolicy: cloudData.isPrivacyPolicy,
            privacySummary: cloudData.privacySummary,
            reputation: cloudData.reputation,
            trustScore: cloudData.trustScore
          };

          if (mode === 'cloud') {
            finalResult = cloudResult;
          }
        } catch (apiErr) {
          console.error('Cloud scanning failed:', apiErr);
          if (mode === 'cloud') {
            throw new Error(`Cloud scan failed. Verify server is running at ${backendUrl}.`);
          } else {
            console.warn('Hybrid mode falling back to local result due to API failure.');
          }
        }
      }

      // If hybrid mode succeeds, inject comparison properties
      if (mode === 'hybrid' && cloudResult) {
        (finalResult as any).cloudResult = cloudResult;
      } else {
        delete (finalResult as any).cloudResult;
      }

      setResult(finalResult);
      setStatus(UI_MESSAGES.READY);
      
      // Update cache
      chrome.storage.local.get(['trustlens_scan_cache'], (store) => {
        const cache = store.trustlens_scan_cache || {};
        cache[url] = {
          data: finalResult,
          cachedAt: Date.now()
        };
        chrome.storage.local.set({ trustlens_scan_cache: cache });
      });

      // Persist results in latest scan
      await chrome.runtime.sendMessage({ type: 'SCAN_RESULTS', data: finalResult });
    } catch (error: any) {
      console.error('Scan Error:', error);
      let userFriendlyError = 'Could not scan this page.';
      if (error.message.includes('Receiving end does not exist') || error.message.includes('Could not establish connection')) {
        userFriendlyError = 'TrustLens content script is not active. Please refresh the page and try again.';
      } else if (error.message) {
        userFriendlyError = error.message;
      }
      setErrorMessage(userFriendlyError);
      setStatus(UI_MESSAGES.ERROR);
    } finally {
      setIsScanning(false);
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!feedbackRating || !result) return;
    setFeedbackStatus('submitting');

    try {
      const payload: any = {
        feedbackType: feedbackRating,
        comment: feedbackComment.trim() || null
      };

      if (result.scanId) {
        payload.scanId = result.scanId;
      } else {
        payload.url = result.url;
        payload.title = result.title;
        payload.ruleScore = result.ruleScore || 0;
        payload.mlScore = result.mlScore || 0;
        payload.finalScore = result.score;
        payload.riskLabel = result.label;
        payload.mlPrediction = result.mlPrediction || 'Safe';
        payload.mlConfidence = result.mlConfidence || 0.0;
      }

      const res = await fetch(`${backendUrl}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error();
      setFeedbackStatus('success');
    } catch (err) {
      console.error('Feedback submission failed:', err);
      setFeedbackStatus('error');
    }
  };

  const hasHybridMismatch = result && (result as any).cloudResult && result.label !== (result as any).cloudResult.label;

  return (
    <div className="popup-container">
      {/* Header section with brand identity */}
      <header className="popup-header">
        <div className="logo-group">
          <Shield size={20} className="logo-icon" />
          <h1 className="logo-text">TrustLens Pro</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="version-badge">v2.0.0</span>
          <button 
            className="settings-toggle-btn"
            onClick={() => setShowSettings(!showSettings)}
            title="Toggle Settings"
          >
            <Settings size={15} />
          </button>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="settings-panel">
          <h2 className="settings-title">Extension Settings</h2>
          
          <div className="settings-group">
            <label>Analysis Mode</label>
            <select 
              className="settings-select"
              value={mode}
              onChange={(e) => saveSettings(e.target.value as any, backendUrl, autoScanEnabled, activeModel)}
            >
              <option value="local">Local Mode (Offline)</option>
              <option value="cloud">Cloud Mode (FastAPI)</option>
              <option value="hybrid">Hybrid Mode (Compare)</option>
            </select>
          </div>

          <div className="settings-group">
            <label>Active NLP Model</label>
            <select 
              className="settings-select"
              value={activeModel}
              onChange={(e) => saveSettings(mode, backendUrl, autoScanEnabled, e.target.value)}
              disabled={mode === 'local'}
            >
              <option value="logistic_regression">Logistic Regression (Lite)</option>
              <option value="minilm_neural_net">MiniLM Neural Net (Deep)</option>
            </select>
          </div>

          <div className="settings-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
            <input 
              type="checkbox" 
              id="autoScanCheck"
              checked={autoScanEnabled}
              onChange={(e) => saveSettings(mode, backendUrl, e.target.checked, activeModel)}
            />
            <label htmlFor="autoScanCheck" style={{ cursor: 'pointer', userSelect: 'none' }}>Enable Background Scanning</label>
          </div>

          <div className="settings-group">
            <label>Backend API URL</label>
            <input 
              type="text" 
              className="settings-input"
              value={backendUrl}
              onChange={(e) => saveSettings(mode, e.target.value, autoScanEnabled, activeModel)}
              placeholder="http://localhost:8000"
            />
          </div>
        </div>
      )}

      {/* Model updates notification banner */}
      {newModelVersion && (
        <div className="update-banner">
          <Info size={16} className="update-icon" />
          <span>New AI Model Available (v{newModelVersion})</span>
        </div>
      )}

      {/* Primary Scanning Button */}
      <button 
        className="scan-btn" 
        onClick={() => handleScan(true)}
        disabled={isScanning}
      >
        {isScanning ? (
          <Loader2 size={16} className="spinner" />
        ) : (
          <Scan size={16} />
        )}
        <span>{isScanning ? 'Analyzing Page...' : result ? 'Rescan Webpage' : 'Scan Webpage'}</span>
      </button>

      {/* Error Card */}
      {errorMessage && (
        <div className="card error-card">
          <AlertCircle size={16} className="error-icon" />
          <span className="error-text">{errorMessage}</span>
        </div>
      )}

      {/* Scan Results Layout */}
      {result && !errorMessage && (
        <div className="results-container" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          
          {/* Tab Selection Row */}
          {result.reputation && (
            <div style={{
              display: 'flex',
              gap: '4px',
              borderBottom: '1px solid var(--border)',
              paddingBottom: '8px',
              marginTop: '4px'
            }}>
              <button
                className={`feedback-btn ${activeTab === 'risk' ? 'active' : ''}`}
                style={{ flex: 1, padding: '4px 0', fontSize: '0.72rem' }}
                onClick={() => setActiveTab('risk')}
              >
                Threat Scanner
              </button>
              <button
                className={`feedback-btn ${activeTab === 'reputation' ? 'active' : ''}`}
                style={{ flex: 1, padding: '4px 0', fontSize: '0.72rem' }}
                onClick={() => setActiveTab('reputation')}
              >
                Reputation & Privacy
              </button>
            </div>
          )}

          {/* TAB 1: THREAT SCANNER */}
          {activeTab === 'risk' && (
            <>
              {/* Hybrid Mode Comparison Card */}
              {mode === 'hybrid' && (result as any).cloudResult && (
                <div className="card hybrid-compare-card">
                  <h3 className="hybrid-header">Hybrid Engine Comparison</h3>
                  <div className="hybrid-grid">
                    <div className="hybrid-column">
                      <span className="hybrid-label">Local Score:</span>
                      <span className="hybrid-value">{result.score}/100 ({result.label})</span>
                    </div>
                    <div className="hybrid-column">
                      <span className="hybrid-label">Cloud Score:</span>
                      <span className="hybrid-value">{(result as any).cloudResult.score}/100 ({(result as any).cloudResult.label})</span>
                    </div>
                  </div>
                  
                  {hasHybridMismatch && (
                    <div className="hybrid-mismatch-banner">
                      ⚠ Discrepancy detected: Local scan indicates {result.label} risk, but Cloud classifier labels it as {(result as any).cloudResult.label}!
                    </div>
                  )}
                </div>
              )}

              {/* Explainable AI (XAI) Explanation block */}
              {result.humanExplanation && (
                <div className="card" style={{ borderLeft: '3px solid var(--safe)', backgroundColor: 'rgba(16, 185, 129, 0.03)' }}>
                  <h3 className="hybrid-header" style={{ color: 'var(--safe)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Eye size={12} />
                    Explainable AI Verdict
                  </h3>
                  <p style={{ fontSize: '0.74rem', color: 'var(--text-light)', lineHeight: '1.4', margin: '4px 0 0 0' }}>
                    {result.humanExplanation}
                  </p>
                </div>
              )}

              {/* XAI Attribution Pill Badges */}
              {result.influentialWords && result.influentialWords.length > 0 && (
                <div className="card">
                  <h4 style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: '600', margin: '0 0 6px 0' }}>
                    Top Influential Risk Keywords (Attribution)
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {result.influentialWords.map((word, i) => (
                      <span key={i} className="badge caution" style={{ padding: '3px 6px', fontSize: '0.65rem' }}>
                        "{word}"
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <RiskCard result={result} />
              <ScoreCard result={result} />
              <MLCard result={result} />
              <IssueList reasons={result.reasons} />
              <KeywordList matchedKeywords={result.matchedKeywords} />

              {/* User Feedback Widget */}
              <div className="card feedback-card">
                <h3 className="feedback-question">Was this prediction correct?</h3>
                <div className="feedback-buttons-row">
                  <button 
                    className={`feedback-btn ${feedbackRating === 'correct' ? 'active' : ''}`}
                    onClick={() => setFeedbackRating('correct')}
                    disabled={feedbackStatus === 'success'}
                  >
                    <ThumbsUp size={14} />
                    <span>Yes</span>
                  </button>
                  <button 
                    className={`feedback-btn ${feedbackRating === 'wrong' ? 'active' : ''}`}
                    onClick={() => setFeedbackRating('wrong')}
                    disabled={feedbackStatus === 'success'}
                  >
                    <ThumbsDown size={14} />
                    <span>No</span>
                  </button>
                </div>

                {feedbackRating && feedbackStatus !== 'success' && (
                  <>
                    <textarea
                      className="feedback-textarea"
                      value={feedbackComment}
                      onChange={(e) => setFeedbackComment(e.target.value)}
                      placeholder="Help us improve. Add a comment (optional)..."
                      maxLength={200}
                    />
                    <button 
                      className="feedback-submit-btn"
                      onClick={handleFeedbackSubmit}
                      disabled={feedbackStatus === 'submitting'}
                    >
                      {feedbackStatus === 'submitting' ? 'Sending...' : 'Submit'}
                    </button>
                  </>
                )}

                {feedbackStatus === 'success' && (
                  <span className="feedback-thankyou">
                    <Check size={14} />
                    Feedback recorded. Thank you!
                  </span>
                )}

                {feedbackStatus === 'error' && (
                  <span style={{ fontSize: '0.72rem', color: 'var(--risky)' }}>
                    Unable to submit feedback. Check server connection.
                  </span>
                )}
              </div>
            </>
          )}

          {/* TAB 2: TECHNICAL REPUTATION & PRIVACY */}
          {activeTab === 'reputation' && result.reputation && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              
              {/* Technical Reputation metrics */}
              <div className="card">
                <h3 className="hybrid-header" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Globe size={14} />
                  Technical Reputation
                </h3>
                
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: 'rgba(15, 23, 42, 0.3)',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  margin: '8px 0'
                }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: '600' }}>Domain Trust Rating:</span>
                  <span style={{ 
                    fontSize: '1rem', 
                    fontWeight: '800', 
                    color: result.trustScore && result.trustScore > 75 ? 'var(--safe)' : result.trustScore && result.trustScore > 40 ? 'var(--caution)' : 'var(--risky)'
                  }}>
                    {result.trustScore}%
                  </span>
                </div>

                <div className="model-meta-grid" style={{ marginTop: '4px', borderTop: 'none', paddingTop: '0' }}>
                  <div className="meta-item" title="HTTPS Security status">
                    {result.reputation.isHttps ? (
                      <Lock size={12} style={{ color: 'var(--safe)' }} />
                    ) : (
                      <Unlock size={12} style={{ color: 'var(--risky)' }} />
                    )}
                    <span className="meta-lbl">SSL:</span>
                    <span className="meta-val">{result.reputation.isHttps ? 'HTTPS Secure' : 'HTTP Unsecure'}</span>
                  </div>

                  <div className="meta-item" title="Domain Age">
                    <Calendar size={12} className="meta-icon" />
                    <span className="meta-lbl">Age:</span>
                    <span className="meta-val">{result.reputation.domainAge}</span>
                  </div>
                </div>

                {result.reputation.isBlacklisted && (
                  <div className="hybrid-mismatch-banner" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--risky)' }}>
                    🚨 Warning: This domain is registered on the TrustLens threat blacklist! High scam risk.
                  </div>
                )}
              </div>

              {/* Privacy Summarizer details */}
              <div className="card">
                <h3 className="hybrid-header" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Shield size={14} />
                  Privacy Policy Summarizer
                </h3>
                
                {result.isPrivacyPolicy && result.privacySummary ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                    <div style={{ fontSize: '0.7rem', borderLeft: '2px solid var(--primary)', paddingLeft: '6px' }}>
                      <strong style={{ color: 'var(--text-light)' }}>📥 Personal Data Collected:</strong>
                      <p style={{ color: 'var(--text-muted)', margin: '2px 0 0 0', lineHeight: '1.35' }}>{result.privacySummary.dataCollected}</p>
                    </div>
                    
                    <div style={{ fontSize: '0.7rem', borderLeft: '2px solid var(--primary)', paddingLeft: '6px' }}>
                      <strong style={{ color: 'var(--text-light)' }}>🤝 Third-Party Sharing:</strong>
                      <p style={{ color: 'var(--text-muted)', margin: '2px 0 0 0', lineHeight: '1.35' }}>{result.privacySummary.thirdPartySharing}</p>
                    </div>

                    <div style={{ fontSize: '0.7rem', borderLeft: '2px solid var(--primary)', paddingLeft: '6px' }}>
                      <strong style={{ color: 'var(--text-light)' }}>🍪 Cookies & Tracking:</strong>
                      <p style={{ color: 'var(--text-muted)', margin: '2px 0 0 0', lineHeight: '1.35' }}>{result.privacySummary.cookies}</p>
                    </div>

                    <div style={{ fontSize: '0.7rem', borderLeft: '2px solid var(--primary)', paddingLeft: '6px' }}>
                      <strong style={{ color: 'var(--text-light)' }}>📢 Advertising & Marketing:</strong>
                      <p style={{ color: 'var(--text-muted)', margin: '2px 0 0 0', lineHeight: '1.35' }}>{result.privacySummary.advertising}</p>
                    </div>

                    <div style={{ fontSize: '0.7rem', borderLeft: '2px solid var(--primary)', paddingLeft: '6px' }}>
                      <strong style={{ color: 'var(--text-light)' }}>⏳ Data Retention Policy:</strong>
                      <p style={{ color: 'var(--text-muted)', margin: '2px 0 0 0', lineHeight: '1.35' }}>{result.privacySummary.dataRetention}</p>
                    </div>

                    <div style={{ fontSize: '0.7rem', borderLeft: '2px solid var(--primary)', paddingLeft: '6px' }}>
                      <strong style={{ color: 'var(--text-light)' }}>🔑 Your Legal Rights:</strong>
                      <p style={{ color: 'var(--text-muted)', margin: '2px 0 0 0', lineHeight: '1.35' }}>{result.privacySummary.userRights}</p>
                    </div>
                  </div>
                ) : (
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '16px',
                    textAlign: 'center',
                    color: 'var(--text-muted)',
                    fontSize: '0.72rem',
                    gap: '4px'
                  }}>
                    <Info size={24} style={{ color: 'var(--border)' }} />
                    <span>No Privacy Policy detected on this page. Navigate to the site's privacy page to see structured highlights.</span>
                  </div>
                )}
              </div>

            </div>
          )}

        </div>
      )}

      {/* Initial state placeholder */}
      {!result && !errorMessage && !isScanning && (
        <div className="empty-state">
          <Shield className="empty-shield" size={40} />
          <p className="empty-text">Click "Scan Webpage" to analyze this site for deceptive dark patterns and privacy risks.</p>
        </div>
      )}

      {/* Small status tracker */}
      {isScanning && (
        <div className="scan-loader">
          <Loader2 className="spinner" size={16} />
          <span>{status}</span>
        </div>
      )}
    </div>
  );
}

export default App;

import { useState, useEffect } from 'react';
import { 
  Shield, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp, 
  RefreshCw, 
  FileText, 
  BarChart2, 
  Key, 
  Globe, 
  ThumbsUp, 
  ThumbsDown 
} from 'lucide-react';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title as ChartTitle,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js modules
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  ChartTitle,
  Tooltip,
  Legend,
  Filler
);

const BACKEND_URL = 'http://localhost:8000';

interface StatsData {
  totalScans: number;
  averageScore: number;
  riskDistribution: {
    Safe: number;
    Caution: number;
    Risky: number;
  };
  feedbackDistribution: {
    correct: number;
    wrong: number;
  };
  mostCommonKeywords: Array<{ keyword: string; count: number }>;
  recentScans: Array<{
    scanId: number;
    domain: string;
    title: string;
    finalScore: number;
    riskLabel: string;
    feedback: 'correct' | 'wrong' | null;
    timestamp: string;
  }>;
  dailyScans: Array<{ date: string; count: number }>;
  commonCategories: Array<{ category: string; count: number }>;
  topDomains: Array<{ domain: string; count: number }>;
}

const defaultStats: StatsData = {
  totalScans: 0,
  averageScore: 0,
  riskDistribution: { Safe: 0, Caution: 0, Risky: 0 },
  feedbackDistribution: { correct: 0, wrong: 0 },
  mostCommonKeywords: [],
  recentScans: [],
  dailyScans: [],
  commonCategories: [],
  topDomains: []
};

function App() {
  const [stats, setStats] = useState<StatsData>(defaultStats);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'logs'>('dashboard');

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/stats`);
      if (!res.ok) {
        throw new Error(`Server returned error status: ${res.status}`);
      }
      const data = await res.json();
      setStats(data);
    } catch (err: any) {
      console.error('Failed to load stats:', err);
      setError('Could not connect to the TrustLens Backend. Make sure it is running on http://localhost:8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  // 1. Line Chart: Daily Scans Configuration
  const lineChartData = {
    labels: stats.dailyScans.map(d => {
      const dateParts = d.date.split('-');
      return `${dateParts[1]}/${dateParts[2]}`; // MM/DD format
    }),
    datasets: [
      {
        label: 'Scans',
        data: stats.dailyScans.map(d => d.count),
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.15)',
        borderWidth: 3,
        tension: 0.35,
        fill: true,
        pointBackgroundColor: '#6366f1',
        pointHoverRadius: 6
      }
    ]
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      x: {
        grid: { color: 'rgba(34, 46, 69, 0.4)' },
        ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } }
      },
      y: {
        grid: { color: 'rgba(34, 46, 69, 0.4)' },
        ticks: { 
          color: '#64748b', 
          font: { family: 'Inter', size: 10 },
          stepSize: 1
        },
        min: 0
      }
    }
  };

  // 2. Doughnut Chart: Risk Level Distribution Configuration
  const doughnutChartData = {
    labels: ['Safe', 'Caution', 'Risky'],
    datasets: [
      {
        data: [
          stats.riskDistribution.Safe,
          stats.riskDistribution.Caution,
          stats.riskDistribution.Risky
        ],
        backgroundColor: [
          'rgba(16, 185, 129, 0.75)', // emerald
          'rgba(245, 158, 11, 0.75)', // amber
          'rgba(239, 68, 68, 0.75)'   // crimson
        ],
        borderColor: '#151c2c',
        borderWidth: 2,
        hoverOffset: 4
      }
    ]
  };

  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#f8fafc',
          font: { family: 'Inter', weight: 'bold' as const, size: 11 },
          padding: 15
        }
      }
    },
    cutout: '70%'
  };

  // 3. Bar Chart: Common Categories Distribution
  const barChartData = {
    labels: stats.commonCategories.map(c => c.category.replace('_', ' ')),
    datasets: [
      {
        data: stats.commonCategories.map(c => c.count),
        backgroundColor: 'rgba(99, 102, 241, 0.7)',
        hoverBackgroundColor: '#6366f1',
        borderRadius: 6
      }
    ]
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#64748b', font: { family: 'Inter', size: 9 } }
      },
      y: {
        grid: { color: 'rgba(34, 46, 69, 0.4)' },
        ticks: { 
          color: '#64748b', 
          font: { family: 'Inter', size: 10 },
          stepSize: 1
        },
        min: 0
      }
    }
  };

  return (
    <div className="dashboard-wrapper">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="logo-container">
          <Shield size={26} className="logo-icon" />
          <span className="logo-text">TrustLens Admin</span>
        </div>
        
        <nav style={{ flexGrow: 1 }}>
          <ul className="nav-list">
            <li>
              <button 
                className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('dashboard')}
              >
                <BarChart2 size={18} />
                <span>Dashboard Analytics</span>
              </button>
            </li>
            <li>
              <button 
                className={`nav-item ${activeTab === 'logs' ? 'active' : ''}`}
                onClick={() => setActiveTab('logs')}
              >
                <FileText size={18} />
                <span>Recent Scan Logs</span>
              </button>
            </li>
          </ul>
        </nav>

        <div className="sidebar-footer">
          <p>TrustLens Full Stack App</p>
          <p style={{ marginTop: '4px', opacity: 0.6 }}>Milestone 4 Engine v1.2.0</p>
        </div>
      </aside>

      {/* Main Panel Area */}
      <main className="main-content">
        <header className="header">
          <div className="title-group">
            <h1>{activeTab === 'dashboard' ? 'Dashboard Analytics' : 'Scan Audit Logs'}</h1>
            <p>
              {activeTab === 'dashboard' 
                ? 'Overview of manipulative pattern detection, classifications, and system health.' 
                : 'Full transaction logs of extension-submitted scans and user feedback inputs.'}
            </p>
          </div>
          
          <button className="refresh-btn" onClick={fetchStats} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'spinner' : ''} />
            <span>Refresh Data</span>
          </button>
        </header>

        {error && (
          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid var(--risky)',
            padding: '16px',
            borderRadius: '10px',
            color: '#fca5a5',
            fontSize: '0.9rem',
            fontWeight: 500,
            marginBottom: '32px'
          }}>
            {error}
          </div>
        )}

        {/* --- TAB: Dashboard View --- */}
        {activeTab === 'dashboard' && (
          <>
            {/* KPI Cards section */}
            <section className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-header">
                  <span>TOTAL WEBPAGE SCANS</span>
                  <div className="kpi-icon-wrapper">
                    <Activity size={16} />
                  </div>
                </div>
                <div className="kpi-value">{loading ? '...' : stats.totalScans}</div>
                <div className="kpi-subtext">Scanned pages since deployment</div>
              </div>

              <div className="kpi-card risky">
                <div className="kpi-header">
                  <span>RISKY WEBSITES FOUND</span>
                  <div className="kpi-icon-wrapper">
                    <AlertTriangle size={16} />
                  </div>
                </div>
                <div className="kpi-value">{loading ? '...' : stats.riskDistribution.Risky}</div>
                <div className="kpi-subtext">High dark pattern concentrations</div>
              </div>

              <div className="kpi-card safe">
                <div className="kpi-header">
                  <span>SAFE WEBSITES VERIFIED</span>
                  <div className="kpi-icon-wrapper">
                    <CheckCircle size={16} />
                  </div>
                </div>
                <div className="kpi-value">{loading ? '...' : stats.riskDistribution.Safe}</div>
                <div className="kpi-subtext">Websites clearing risk thresholds</div>
              </div>

              <div className="kpi-card">
                <div className="kpi-header">
                  <span>AVERAGE RISK SCORE</span>
                  <div className="kpi-icon-wrapper">
                    <TrendingUp size={16} />
                  </div>
                </div>
                <div className="kpi-value">{loading ? '...' : `${stats.averageScore}/100`}</div>
                <div className="kpi-subtext">Calculated system-wide mean</div>
              </div>
            </section>

            {/* Primary Charts section */}
            <section className="charts-grid">
              <div className="chart-card">
                <h3 className="chart-title">Webpage Scans Frequency (Last 7 Days)</h3>
                <div className="chart-container">
                  {loading ? (
                    <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Loading...</div>
                  ) : (
                    <Line data={lineChartData} options={lineChartOptions} />
                  )}
                </div>
              </div>

              <div className="chart-card">
                <h3 className="chart-title">Risk Label Distribution</h3>
                <div className="chart-container">
                  {loading ? (
                    <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Loading...</div>
                  ) : (
                    <Doughnut data={doughnutChartData} options={doughnutChartOptions} />
                  )}
                </div>
              </div>
            </section>

            {/* Statistics Splitting grid */}
            <section className="stats-split-grid">
              <div className="chart-card">
                <h3 className="chart-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart2 size={16} className="logo-icon" />
                  Deceptive Categories
                </h3>
                <div className="chart-container" style={{ height: '200px' }}>
                  {loading ? (
                    <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Loading...</div>
                  ) : (
                    <Bar data={barChartData} options={barChartOptions} />
                  )}
                </div>
              </div>

              <div className="chart-card">
                <h3 className="chart-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Key size={16} className="logo-icon" />
                  Common Matched Keywords
                </h3>
                <ul className="stats-card-list keywords">
                  {loading ? (
                    <li className="stats-list-item">Loading keywords...</li>
                  ) : stats.mostCommonKeywords.length === 0 ? (
                    <li className="stats-list-item" style={{ color: 'var(--text-muted)' }}>No keywords recorded yet.</li>
                  ) : (
                    stats.mostCommonKeywords.map((kw, i) => (
                      <li key={i} className="stats-list-item">
                        <span className="stats-item-name">"{kw.keyword}"</span>
                        <span className="stats-item-value">{kw.count} hits</span>
                      </li>
                    ))
                  )}
                </ul>
              </div>

              <div className="chart-card">
                <h3 className="chart-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Globe size={16} className="logo-icon" />
                  Top Scanned Domains
                </h3>
                <ul className="stats-card-list">
                  {loading ? (
                    <li className="stats-list-item">Loading domains...</li>
                  ) : stats.topDomains.length === 0 ? (
                    <li className="stats-list-item" style={{ color: 'var(--text-muted)' }}>No domains scanned yet.</li>
                  ) : (
                    stats.topDomains.map((dom, i) => (
                      <li key={i} className="stats-list-item">
                        <span className="stats-item-name" style={{ fontFamily: 'monospace' }}>{dom.domain}</span>
                        <span className="stats-item-value" style={{ color: 'var(--safe)' }}>{dom.count} times</span>
                      </li>
                    ))
                  )}
                </ul>
              </div>
            </section>
          </>
        )}

        {/* --- TAB: Logs View --- */}
        {(activeTab === 'logs' || activeTab === 'dashboard') && (
          <section className="table-card" style={{ marginTop: activeTab === 'logs' ? '0' : '32px' }}>
            <div className="table-header">
              <h3 className="table-title">Recent Webpage Scans & Feedback Ratings</h3>
              <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <span>👍 Positive Ratings: {stats.feedbackDistribution.correct}</span>
                <span>👎 Negative Ratings: {stats.feedbackDistribution.wrong}</span>
              </div>
            </div>

            <div className="scan-table-wrapper">
              <table className="scan-table">
                <thead>
                  <tr>
                    <th>TIMESTAMP</th>
                    <th>DOMAIN</th>
                    <th>WEBPAGE TITLE</th>
                    <th>RISK SCORE</th>
                    <th>VERDICT</th>
                    <th>USER RATING</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                        Loading transaction tables...
                      </td>
                    </tr>
                  ) : stats.recentScans.length === 0 ? (
                    <tr>
                      <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                        No records logged in the database yet. Scan some websites using the extension.
                      </td>
                    </tr>
                  ) : (
                    stats.recentScans.map((scan) => (
                      <tr key={scan.scanId}>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>{scan.timestamp}</td>
                        <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>{scan.domain}</td>
                        <td style={{ maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={scan.title}>
                          {scan.title}
                        </td>
                        <td style={{ fontWeight: 800 }}>{scan.finalScore}/100</td>
                        <td>
                          <span className={`badge ${scan.riskLabel.toLowerCase()}`}>
                            {scan.riskLabel}
                          </span>
                        </td>
                        <td>
                          {scan.feedback === 'correct' && (
                            <span className="badge thumbs-up" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                              <ThumbsUp size={10} />
                              Correct
                            </span>
                          )}
                          {scan.feedback === 'wrong' && (
                            <span className="badge thumbs-down" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                              <ThumbsDown size={10} />
                              Inaccurate
                            </span>
                          )}
                          {!scan.feedback && (
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', paddingLeft: '8px' }}>—</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;

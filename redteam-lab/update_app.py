import re

app_code = """import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { authService, campaignService, taskService, aiService, dashboardService } from './services/api';
import {
  Shield, Activity, Target, Terminal, LogOut, Cpu, FileText,
  CheckCircle, Clock, Trash2, Eye, AlertTriangle, ChevronRight,
  ExternalLink, Download, X, RefreshCw, Plus, Zap, BarChart2,
  Radio, Lock, Globe, TrendingUp, AlertCircle
} from 'lucide-react';
import {
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line, Area, AreaChart
} from 'recharts';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/* ─── Design Tokens ─────────────────────────────────────────── */
const T = {
  bg:           '#080c14',
  surface:      '#0d1220',
  surfaceAlt:   '#111827',
  border:       'rgba(255,255,255,0.07)',
  borderHover:  'rgba(255,255,255,0.14)',
  primary:      '#f43f5e',
  primaryDim:   'rgba(244,63,94,0.15)',
  primaryGlow:  'rgba(244,63,94,0.35)',
  accent:       '#6366f1',
  accentDim:    'rgba(99,102,241,0.15)',
  textPrimary:  '#f1f5f9',
  textMuted:    '#64748b',
  textSub:      '#94a3b8',
  success:      '#10b981',
  successDim:   'rgba(16,185,129,0.12)',
  warning:      '#f59e0b',
  warningDim:   'rgba(245,158,11,0.12)',
  danger:       '#ef4444',
  dangerDim:    'rgba(239,68,68,0.12)',
  critical:     '#ff3b3b',
  criticalDim:  'rgba(255,59,59,0.12)',
  purple:       '#a855f7',
  purpleDim:    'rgba(168,85,247,0.12)',
};

/* ─── Global Styles (injected once) ─────────────────────────── */
const GlobalStyles = () => (
  <style>{`
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: ${T.bg};
      color: ${T.textPrimary};
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
    }

    /* scrollbar */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: ${T.border}; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: ${T.borderHover}; }

    /* typography helpers */
    .mono { font-family: 'JetBrains Mono', 'Fira Code', monospace; }
    .text-muted { color: ${T.textMuted}; }
    .text-sub { color: ${T.textSub}; font-size: 0.85rem; }

    /* gradient text */
    .grad-primary {
      background: linear-gradient(135deg, #f43f5e 0%, #fb923c 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .grad-accent {
      background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }

    /* card */
    .card {
      background: ${T.surface};
      border: 1px solid ${T.border};
      border-radius: 12px;
      padding: 20px 24px;
      transition: border-color 0.2s ease;
    }
    .card:hover { border-color: ${T.borderHover}; }
    .card-sm { padding: 14px 16px; border-radius: 10px; }

    /* status pill */
    .pill {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 3px 10px; border-radius: 20px;
      font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase;
    }
    .pill.success { background: ${T.successDim}; color: ${T.success}; }
    .pill.warning { background: ${T.warningDim}; color: ${T.warning}; }
    .pill.danger  { background: ${T.dangerDim};  color: ${T.danger};  }
    .pill.critical{ background: ${T.criticalDim};color: ${T.critical};}
    .pill.accent  { background: ${T.accentDim};  color: ${T.accent};  }
    .pill.primary { background: ${T.primaryDim}; color: ${T.primary}; }
    .pill.purple  { background: ${T.purpleDim};  color: ${T.purple};  }
    .pill.muted   { background: rgba(255,255,255,0.06); color: ${T.textSub}; }

    /* dot indicator */
    .dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
    .dot.success { background: ${T.success}; }
    .dot.warning { background: ${T.warning}; box-shadow: 0 0 6px ${T.warning}; }
    .dot.danger  { background: ${T.danger}; }
    .dot.running { background: ${T.warning}; animation: pulse 1.5s ease infinite; }
    @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

    /* buttons */
    .btn {
      display: inline-flex; align-items: center; gap: 7px;
      padding: 9px 18px; border-radius: 8px; font-size: 0.875rem;
      font-weight: 500; cursor: pointer; border: none;
      transition: all 0.18s ease; white-space: nowrap;
    }
    .btn-ghost {
      background: transparent; color: ${T.textSub};
      border: 1px solid ${T.border};
    }
    .btn-ghost:hover { background: rgba(255,255,255,0.05); color: ${T.textPrimary}; border-color: ${T.borderHover}; }
    .btn-red {
      background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
      color: #fff; box-shadow: 0 4px 14px ${T.primaryGlow};
    }
    .btn-red:hover { filter: brightness(1.08); transform: translateY(-1px); }
    .btn-red:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }
    .btn-icon {
      padding: 7px; border-radius: 8px; background: transparent;
      border: 1px solid ${T.border}; color: ${T.textMuted};
      cursor: pointer; transition: all 0.18s; display: inline-flex; align-items: center; justify-content: center;
    }
    .btn-icon:hover { background: rgba(255,255,255,0.06); color: ${T.textPrimary}; border-color: ${T.borderHover}; }
    .btn-icon.danger:hover { color: ${T.danger}; border-color: rgba(239,68,68,0.4); }

    /* inputs */
    .field {
      width: 100%; background: rgba(0,0,0,0.25);
      border: 1px solid ${T.border}; color: ${T.textPrimary};
      padding: 11px 14px; border-radius: 8px; font-family: inherit;
      font-size: 0.875rem; outline: none; transition: all 0.2s;
    }
    .field::placeholder { color: ${T.textMuted}; }
    .field:focus { border-color: ${T.primary}; box-shadow: 0 0 0 3px ${T.primaryDim}; background: rgba(0,0,0,0.35); }

    /* divider */
    .divider { border: none; border-top: 1px solid ${T.border}; margin: 20px 0; }

    /* fade-in */
    @keyframes fadeUp { from{opacity:0;transform:translateY(12px);} to{opacity:1;transform:none;} }
    .fade-in { animation: fadeUp 0.35s ease forwards; }

    /* spin */
    @keyframes spin { to { transform: rotate(360deg); } }
    .spin { animation: spin 1s linear infinite; }

    /* nav active */
    .nav-item {
      display: flex; align-items: center; gap: 10px;
      padding: 9px 14px; border-radius: 8px; font-size: 0.875rem;
      font-weight: 500; cursor: pointer; border: none;
      background: transparent; color: ${T.textMuted};
      transition: all 0.18s ease; width: 100%; text-align: left;
    }
    .nav-item:hover { background: rgba(255,255,255,0.05); color: ${T.textPrimary}; }
    .nav-item.active { background: ${T.primaryDim}; color: ${T.primary}; }

    /* table */
    .data-table { width: 100%; border-collapse: collapse; }
    .data-table th {
      padding: 10px 14px; text-align: left; font-size: 0.72rem;
      font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
      color: ${T.textMuted}; border-bottom: 1px solid ${T.border};
    }
    .data-table td { padding: 13px 14px; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.875rem; }
    .data-table tr:last-child td { border-bottom: none; }
    .data-table tr:hover td { background: rgba(255,255,255,0.02); }

    /* mitre badge */
    .mitre-badge {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 3px 8px; border-radius: 5px; font-size: 0.72rem; font-weight: 600;
      background: rgba(168,85,247,0.15); color: #c084fc;
      border: 1px solid rgba(168,85,247,0.3); text-decoration: none;
    }
    .mitre-badge:hover { background: rgba(168,85,247,0.25); }

    /* stat ring labels */
    .severity-row {
      display: flex; align-items: center; gap: 10px;
      padding: 8px 12px; border-radius: 8px;
      background: rgba(0,0,0,0.2); border: 1px solid ${T.border};
      font-size: 0.83rem;
    }
    .sev-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    
    /* Markdown Body Styles - Document Preview Format */
    .markdown-body {
      background: transparent !important;
      color: #1a1a2e !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 {
      border-bottom: 1px solid #eaecef;
      padding-bottom: 0.3em;
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
      color: #1a1a2e !important;
    }
    .markdown-body table {
      border-spacing: 0;
      border-collapse: collapse;
      width: 100%;
      margin-top: 0;
      margin-bottom: 16px;
    }
    .markdown-body table th, .markdown-body table td {
      padding: 6px 13px;
      border: 1px solid #dfe2e5;
    }
    .markdown-body table tr {
      background-color: #fff;
      border-top: 1px solid #c6cbd1;
    }
    .markdown-body table tr:nth-child(2n) {
      background-color: #f6f8fa;
    }
    .markdown-body pre {
      background-color: #f6f8fa;
      border-radius: 3px;
      padding: 16px;
      overflow: auto;
      color: #1a1a2e;
    }
    .markdown-body code {
      background-color: rgba(27,31,35,0.05);
      border-radius: 3px;
      padding: 0.2em 0.4em;
      color: #1a1a2e;
    }
    .markdown-body pre code {
      background-color: transparent;
      padding: 0;
    }
  `}</style>
);

/* ─── Severity color map ────────────────────────────────────── */
const SEV_COLORS = {
  critical: '#ff3b3b',
  high:     '#f97316',
  medium:   '#f59e0b',
  low:      '#eab308',
  info:     '#6366f1',
};

/* ─── Stat Card ─────────────────────────────────────────────── */
const StatCard = ({ icon: Icon, label, value, color = T.primary, dim, trend }) => (
  <div className="card fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 12, minWidth: 0 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div style={{ padding: 10, borderRadius: 10, background: dim || T.primaryDim }}>
        <Icon size={20} color={color} />
      </div>
      {trend !== undefined && (
        <span style={{ fontSize: '0.75rem', color: trend >= 0 ? T.success : T.danger, display: 'flex', alignItems: 'center', gap: 3 }}>
          <TrendingUp size={12} /> {trend >= 0 ? '+' : ''}{trend}%
        </span>
      )}
    </div>
    <div>
      <p style={{ fontSize: '0.75rem', color: T.textMuted, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>{label}</p>
      <p style={{ fontSize: '1.9rem', fontWeight: 700, lineHeight: 1 }}>{value}</p>
    </div>
  </div>
);

/* ─── Section Header ─────────────────────────────────────────── */
const SectionHeader = ({ title, subtitle, action }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
    <div>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 2 }}>{title}</h3>
      {subtitle && <p className="text-sub">{subtitle}</p>}
    </div>
    {action}
  </div>
);

/* ─── Empty State ────────────────────────────────────────────── */
const EmptyState = ({ icon: Icon = Shield, message, cta }) => (
  <div style={{ textAlign: 'center', padding: '48px 0' }}>
    <div style={{ display: 'inline-flex', padding: 16, borderRadius: 16, background: T.primaryDim, marginBottom: 16 }}>
      <Icon size={28} color={T.primary} />
    </div>
    <p style={{ color: T.textMuted, marginBottom: cta ? 16 : 0 }}>{message}</p>
    {cta}
  </div>
);

/* ─── Severity Legend Row ────────────────────────────────────── */
const SeverityRow = ({ name, value, color, total }) => {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div className="severity-row">
      <span className="sev-dot" style={{ background: color }} />
      <span style={{ flex: 1, color: T.textSub }}>{name}</span>
      <div style={{ width: 80, height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 2 }} />
      </div>
      <span className="mono" style={{ fontSize: '0.8rem', minWidth: 28, textAlign: 'right' }}>{value}</span>
    </div>
  );
};

/* ─── Tooltip style ─────────────────────────────────────────── */
const chartTooltip = {
  contentStyle: {
    background: T.surfaceAlt, border: `1px solid ${T.border}`,
    borderRadius: 8, color: T.textPrimary, fontSize: 12,
  },
  itemStyle: { color: T.textPrimary },
};

/* ─── Login ──────────────────────────────────────────────────── */
const Login = ({ setAuth }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await authService.login(username, password);
      setAuth(true);
      navigate('/');
    } catch {
      setError('Invalid credentials. Try again.');
    } finally { setLoading(false); }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: `radial-gradient(ellipse at 20% 60%, rgba(244,63,94,0.07) 0%, transparent 50%),
                   radial-gradient(ellipse at 80% 20%, rgba(99,102,241,0.07) 0%, transparent 50%),
                   ${T.bg}`
    }}>
      <div className="card fade-in" style={{ width: 400, padding: 40 }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <div style={{
            display: 'inline-flex', padding: 16, borderRadius: 16,
            background: T.primaryDim, border: `1px solid rgba(244,63,94,0.2)`, marginBottom: 20
          }}>
            <Shield size={32} color={T.primary} />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 6 }}>
            RedTeam<span className="grad-primary"> Lab</span>
          </h1>
          <p className="text-sub">Authorized personnel only. All sessions are logged.</p>
        </div>

        {error && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            background: T.dangerDim, border: `1px solid rgba(239,68,68,0.2)`,
            borderRadius: 8, padding: '10px 14px', marginBottom: 20, fontSize: '0.875rem', color: T.danger
          }}>
            <AlertCircle size={15} /> {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <label style={{ fontSize: '0.78rem', color: T.textMuted, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 6 }}>
            Username
          </label>
          <input className="field" type="text" placeholder="operator" value={username}
            onChange={e => setUsername(e.target.value)} required style={{ marginBottom: 14 }} />

          <label style={{ fontSize: '0.78rem', color: T.textMuted, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 6 }}>
            Password
          </label>
          <input className="field" type="password" placeholder="••••••••" value={password}
            onChange={e => setPassword(e.target.value)} required style={{ marginBottom: 28 }} />

          <button type="submit" className="btn btn-red" style={{ width: '100%', justifyContent: 'center', padding: '11px 18px' }} disabled={loading}>
            {loading ? <RefreshCw size={16} className="spin" /> : <Terminal size={16} />}
            {loading ? 'Authenticating…' : 'Initialize Session'}
          </button>
        </form>

        <div style={{ marginTop: 24, textAlign: 'center' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: '0.78rem', color: T.textMuted }}>
            <Lock size={12} /> End-to-end encrypted
          </span>
        </div>
      </div>
    </div>
  );
};

/* ─── Sidebar ────────────────────────────────────────────────── */
const Sidebar = ({ setAuth }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const handleLogout = () => { authService.logout(); setAuth(false); navigate('/login'); };

  const navItems = [
    { path: '/', icon: BarChart2, label: 'Dashboard' },
    { path: '/campaigns', icon: Target, label: 'Campaigns' },
  ];

  return (
    <aside style={{
      width: 220, background: T.surface,
      borderRight: `1px solid ${T.border}`,
      display: 'flex', flexDirection: 'column',
      padding: '0 12px 20px', flexShrink: 0
    }}>
      {/* Brand */}
      <div style={{ padding: '22px 4px 28px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ padding: 7, borderRadius: 9, background: T.primaryDim }}>
          <Shield size={18} color={T.primary} />
        </div>
        <span style={{ fontWeight: 700, fontSize: '0.95rem', letterSpacing: '-0.01em' }}>
          Red<span className="grad-primary">Team</span>
        </span>
      </div>

      {/* Status indicator */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '8px 10px', borderRadius: 8,
        background: T.successDim, border: `1px solid rgba(16,185,129,0.15)`,
        marginBottom: 20, fontSize: '0.78rem', color: T.success
      }}>
        <span className="dot running" style={{ background: T.success, boxShadow: `0 0 6px ${T.success}` }} />
        Systems Operational
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
        <p style={{ fontSize: '0.68rem', fontWeight: 600, color: T.textMuted, textTransform: 'uppercase', letterSpacing: '0.08em', padding: '0 10px', marginBottom: 6 }}>Navigation</p>
        {navItems.map(({ path, icon: Icon, label }) => (
          <button key={path} className={`nav-item ${location.pathname === path ? 'active' : ''}`}
            onClick={() => navigate(path)}>
            <Icon size={16} /> {label}
          </button>
        ))}
      </nav>

      <hr className="divider" style={{ margin: '12px 0' }} />
      <button className="nav-item" onClick={handleLogout}
        style={{ color: T.danger }}>
        <LogOut size={16} /> Terminate Session
      </button>
    </aside>
  );
};

/* ─── Layout ─────────────────────────────────────────────────── */
const Layout = ({ children, setAuth }) => (
  <div style={{ display: 'flex', minHeight: '100vh' }}>
    <Sidebar setAuth={setAuth} />
    <main style={{ flex: 1, overflowY: 'auto', padding: '32px 36px', minWidth: 0,
      background: `radial-gradient(ellipse at 5% 0%, rgba(244,63,94,0.04) 0%, transparent 40%)` }}>
      {children}
    </main>
  </div>
);

/* ─── AI Report Modal ────────────────────────────────────────── */
const ReportModal = ({ analysis, onClose, onDownload }) => (
  <div style={{
    position: 'fixed', inset: 0, zIndex: 200,
    background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 32
  }}>
    <div className="card fade-in" style={{
      width: '100%', maxWidth: 860, maxHeight: '88vh',
      display: 'flex', flexDirection: 'column',
      borderLeft: `3px solid ${T.primary}`, padding: 0
    }}>
      {/* Modal header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 24px', borderBottom: `1px solid ${T.border}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <FileText size={18} color={T.primary} />
          <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{analysis.title}</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-ghost" style={{ padding: '7px 14px' }} onClick={onDownload}>
            <Download size={14} /> Export .md
          </button>
          <button className="btn-icon" onClick={onClose}><X size={16} /></button>
        </div>
      </div>
      {/* Modal body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '28px 32px', background: '#f1f5f9' }}>
        <div className="markdown-body" style={{
          maxWidth: 760, margin: '0 auto', background: '#fff',
          borderRadius: 8, padding: '40px 48px',
          boxShadow: '0 1px 12px rgba(0,0,0,0.08)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          color: '#1a1a2e', lineHeight: 1.7, fontSize: '0.92rem',
        }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {analysis.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  </div>
);

/* ─── Analyzing Overlay ──────────────────────────────────────── */
const AnalyzingOverlay = () => (
  <div style={{
    position: 'fixed', inset: 0, zIndex: 200,
    background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)',
    display: 'flex', alignItems: 'center', justifyContent: 'center'
  }}>
    <div className="card fade-in" style={{ maxWidth: 420, width: '100%', borderLeft: `3px solid ${T.warning}`, padding: '28px 32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
        <RefreshCw size={22} color={T.warning} className="spin" />
        <span style={{ fontWeight: 600, color: T.warning }}>Compiling AI engagement report…</span>
      </div>
      <p className="text-sub">The Ollama model is analyzing findings. This typically takes 1–3 minutes depending on complexity.</p>
      <div style={{ marginTop: 16, height: 2, borderRadius: 1, background: T.border, overflow: 'hidden' }}>
        <div style={{ height: '100%', background: T.warning, width: '60%', animation: 'loading 1.8s ease infinite alternate' }} />
      </div>
      <style>{`@keyframes loading { from{transform:translateX(-60%);} to{transform:translateX(130%);} }`}</style>
    </div>
  </div>
);

/* ─── Dashboard ──────────────────────────────────────────────── */
const Dashboard = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [recentTasks, setRecentTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
    const iv = setInterval(fetchData, 5000);
    return () => clearInterval(iv);
  }, []);

  const fetchData = async () => {
    try {
      const all = await campaignService.getAll();
      setCampaigns(all);
      try { setStats(await dashboardService.getStats()); } catch {}
      if (all.length > 0) {
        const latest = all[all.length - 1];
        setRecentTasks(await taskService.getByCampaign(latest.id));
      }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this engagement and all associated data?')) return;
    try {
      await campaignService.delete(id);
      fetchData();
      if (selectedAnalysis?.campaignId === id) setSelectedAnalysis(null);
    } catch { alert('Failed to delete engagement'); }
  };

  const handleGenerateReport = async (campaign) => {
    setIsAnalyzing(true); setSelectedAnalysis(null);
    try {
      const res = await aiService.generateReport(campaign.id);
      setSelectedAnalysis({
        title: `Engagement Report — ${campaign.name} · ${campaign.target}`,
        campaignId: campaign.id,
        content: res.report || JSON.stringify(res, null, 2),
      });
    } catch {
      setSelectedAnalysis({
        title: 'Analysis Error',
        campaignId: campaign.id,
        content: 'Error running analysis. The Ollama model may still be loading, or no findings exist yet for this engagement.',
      });
    }
    setIsAnalyzing(false);
  };

  const handleDownloadReport = () => {
    if (!selectedAnalysis) return;
    const blob = new Blob([selectedAnalysis.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement('a'), { href: url, download: `Report_${selectedAnalysis.campaignId}.md` });
    a.click(); URL.revokeObjectURL(url);
  };

  const severityData = stats ? [
    { name: 'Critical', value: stats.findings.severity.critical || 0, color: SEV_COLORS.critical },
    { name: 'High',     value: stats.findings.severity.high     || 0, color: SEV_COLORS.high     },
    { name: 'Medium',   value: stats.findings.severity.medium   || 0, color: SEV_COLORS.medium   },
    { name: 'Low',      value: stats.findings.severity.low      || 0, color: SEV_COLORS.low      },
    { name: 'Info',     value: stats.findings.severity.info     || 0, color: SEV_COLORS.info     },
  ].filter(d => d.value > 0) : [];

  const totalFindings = severityData.reduce((a, d) => a + d.value, 0);

  const runningCount = campaigns.filter(c => c.status === 'running').length;
  const completedCount = campaigns.filter(c => c.status === 'completed').length;

  return (
    <div className="fade-in" style={{ paddingBottom: 48 }}>
      {/* Page header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: '1.65rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 6 }}>
          Executive Dashboard
        </h1>
        <p className="text-sub">Real-time security posture and engagement intelligence.</p>
      </div>

      {/* ── Stat cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 16, marginBottom: 28 }}>
        <StatCard icon={Target}       label="Total Engagements" value={stats?.campaigns.total ?? 0}    color={T.primary}  dim={T.primaryDim} />
        <StatCard icon={AlertTriangle} label="Total Findings"    value={stats?.findings.total ?? 0}     color={T.danger}   dim={T.dangerDim}  />
        <StatCard icon={Radio}         label="Active Operations" value={runningCount}                    color={T.warning}  dim={T.warningDim} />
        <StatCard icon={CheckCircle}   label="Completed"         value={completedCount}                  color={T.success}  dim={T.successDim} />
      </div>

      {/* ── Charts row ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
        {/* Severity donut */}
        <div className="card">
          <SectionHeader title="Risk severity distribution" subtitle="All engagements combined" />
          {severityData.length > 0 ? (
            <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
              <div style={{ width: 160, height: 160, flexShrink: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={severityData} cx="50%" cy="50%" innerRadius={48} outerRadius={68}
                      paddingAngle={3} dataKey="value" stroke="none">
                      {severityData.map((e, i) => <Cell key={i} fill={e.color} />)}
                    </Pie>
                    <RechartsTooltip {...chartTooltip} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}>
                {severityData.map(d => (
                  <SeverityRow key={d.name} name={d.name} value={d.value} color={d.color} total={totalFindings} />
                ))}
              </div>
            </div>
          ) : (
            <EmptyState icon={BarChart2} message="No vulnerability data yet." />
          )}
        </div>

        {/* MITRE ATT&CK */}
        <div className="card">
          <SectionHeader title="Top MITRE ATT&CK techniques" subtitle="By detection frequency" />
          {stats?.top_mitre?.length > 0 ? (
            <div style={{ height: 180 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.top_mitre.slice(0, 6)} layout="vertical" margin={{ left: 0, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={T.border} horizontal={false} />
                  <XAxis type="number" stroke={T.textMuted} tick={{ fontSize: 11, fill: T.textMuted }} />
                  <YAxis dataKey="id" type="category" width={70} tick={{ fontSize: 11, fill: T.textSub, fontFamily: 'monospace' }} />
                  <RechartsTooltip {...chartTooltip} />
                  <Bar dataKey="count" fill={T.accent} radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState icon={Shield} message="No MITRE techniques mapped yet." />
          )}
        </div>
      </div>

      {/* ── Historical Targets table ── */}
      <div className="card" style={{ marginBottom: 28 }}>
        <SectionHeader
          title="Historical engagements"
          subtitle={`${campaigns.length} total on record`}
          action={
            <button className="btn btn-red" style={{ padding: '7px 16px' }} onClick={() => navigate('/campaigns')}>
              <Plus size={14} /> New Campaign
            </button>
          }
        />
        {campaigns.length === 0 ? (
          <EmptyState message="No engagements recorded yet." cta={
            <button className="btn btn-red" onClick={() => navigate('/campaigns')}>
              <Plus size={14} /> Deploy first campaign
            </button>
          } />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Target</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.slice().reverse().map(c => (
                  <tr key={c.id}>
                    <td style={{ fontWeight: 500 }}>{c.name}</td>
                    <td className="mono text-muted" style={{ fontSize: '0.83rem' }}>{c.target}</td>
                    <td>
                      <span className={`pill ${c.status === 'completed' ? 'success' : c.status === 'running' ? 'warning' : 'muted'}`}>
                        <span className={`dot ${c.status === 'running' ? 'running' : ''}`}
                          style={{ background: c.status === 'completed' ? T.success : c.status === 'running' ? T.warning : T.textMuted }} />
                        {c.status}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: 6, justifyContent: 'flex-end' }}>
                        <button className="btn btn-ghost" style={{ padding: '5px 12px', fontSize: '0.8rem' }}
                          onClick={() => handleGenerateReport(c)} disabled={isAnalyzing}>
                          <Cpu size={13} /> AI Analysis
                        </button>
                        <button className="btn-icon danger" onClick={() => handleDelete(c.id)}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Recent task feed ── */}
      {recentTasks.length > 0 && (
        <div className="card">
          <SectionHeader title="Latest operation tasks" subtitle="From most recent engagement" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recentTasks.slice(0, 6).map(task => (
              <div key={task.id} style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '10px 14px', borderRadius: 8,
                background: 'rgba(0,0,0,0.2)', border: `1px solid ${T.border}`
              }}>
                <div style={{ padding: 6, borderRadius: 6, background: task.status === 'completed' ? T.successDim : task.status === 'failed' ? T.dangerDim : T.warningDim }}>
                  {task.status === 'completed' ? <CheckCircle size={14} color={T.success} /> : task.status === 'failed' ? <AlertCircle size={14} color={T.danger} /> : <Clock size={14} color={T.warning} />}
                </div>
                <span className="mono" style={{ fontSize: '0.83rem', flex: 1 }}>{task.module}</span>
                {task.mitre?.id && task.mitre.id !== 'T0000' && (
                  <a href={`https://attack.mitre.org/techniques/${task.mitre.id.replace('.', '/')}/`}
                    target="_blank" rel="noreferrer" className="mitre-badge">
                    <Shield size={10} /> {task.mitre.id}
                  </a>
                )}
                <span className={`pill ${task.status === 'completed' ? 'success' : task.status === 'failed' ? 'danger' : 'warning'}`}>
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {isAnalyzing && <AnalyzingOverlay />}
      {selectedAnalysis && !isAnalyzing && (
        <ReportModal analysis={selectedAnalysis} onClose={() => setSelectedAnalysis(null)} onDownload={handleDownloadReport} />
      )}
    </div>
  );
};

/* ─── Task Card ─────────────────────────────────────────────── */
const TaskCard = ({ task, onAnalyze, isAnalyzing }) => {
  const getMitreUrl = (id) => {
    const parts = id.split('.');
    return parts.length > 1
      ? `https://attack.mitre.org/techniques/${parts[0]}/${parts[1]}/`
      : `https://attack.mitre.org/techniques/${id}/`;
  };

  const statusColor = { completed: T.success, failed: T.danger, running: T.warning };
  const statusDim   = { completed: T.successDim, failed: T.dangerDim, running: T.warningDim };

  return (
    <div style={{
      background: 'rgba(0,0,0,0.2)', border: `1px solid ${T.border}`,
      borderRadius: 10, padding: '14px 16px', transition: 'border-color 0.2s'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0, flex: 1 }}>
          <div style={{ padding: 6, borderRadius: 6, background: statusDim[task.status] || T.accentDim, flexShrink: 0 }}>
            {task.status === 'completed' ? <CheckCircle size={13} color={T.success} />
              : task.status === 'failed' ? <AlertCircle size={13} color={T.danger} />
              : <Clock size={13} color={T.warning} />}
          </div>
          <span className="mono" style={{ fontSize: '0.83rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{task.module}</span>
          {task.mitre?.id && task.mitre.id !== 'T0000' && (
            <a href={getMitreUrl(task.mitre.id)} target="_blank" rel="noreferrer" className="mitre-badge" title={task.mitre.name}>
              <Shield size={9} /> {task.mitre.id}
            </a>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          <span className={`pill ${task.status === 'completed' ? 'success' : task.status === 'failed' ? 'danger' : 'warning'}`}>
            {task.status}
          </span>
          <button className="btn btn-ghost" style={{ padding: '5px 10px', fontSize: '0.78rem' }}
            onClick={() => onAnalyze(task.id)}
            disabled={task.status !== 'completed' || isAnalyzing === task.id}>
            {isAnalyzing === task.id ? <RefreshCw size={12} className="spin" /> : <Cpu size={12} />}
            {isAnalyzing === task.id ? ' Analyzing…' : ' Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
};

/* ─── Campaigns ──────────────────────────────────────────────── */
const Campaigns = () => {
  const [name, setName] = useState('');
  const [target, setTarget] = useState('');
  const [campaignId, setCampaignId] = useState(null);
  const [campaignName, setCampaignName] = useState('');
  const [tasks, setTasks] = useState([]);
  const [analyzingTask, setAnalyzingTask] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState('');
  const [step, setStep] = useState('idle'); // idle | ready | running

  useEffect(() => {
    if (!campaignId) return;
    fetchTasks();
    const iv = setInterval(fetchTasks, 3000);
    return () => clearInterval(iv);
  }, [campaignId]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await campaignService.create(name, target);
      setCampaignId(res.id);
      setCampaignName(name);
      setStep('ready');
      setName(''); setTarget('');
    } catch { alert('Error creating campaign'); }
  };

  const handleStart = async () => {
    if (!campaignId) return;
    try {
      await campaignService.start(campaignId);
      setStep('running');
      fetchTasks();
    } catch { alert('Error starting campaign'); }
  };

  const fetchTasks = async () => {
    if (!campaignId) return;
    try { setTasks(await taskService.getByCampaign(campaignId)); }
    catch (e) { console.error(e); }
  };

  const handleAnalyzeTask = async (taskId) => {
    setAnalyzingTask(taskId); setAiAnalysis('');
    try {
      const res = await aiService.analyzeTask(taskId);
      setAiAnalysis(res.analysis || JSON.stringify(res, null, 2));
    } catch {
      setAiAnalysis('Error running analysis. The task may not be complete, or the Ollama model is still loading (this can take 1–3 minutes).');
    }
    setAnalyzingTask(null);
  };

  const completedCount = tasks.filter(t => t.status === 'completed').length;
  const failedCount    = tasks.filter(t => t.status === 'failed').length;
  const pendingCount   = tasks.filter(t => t.status !== 'completed' && t.status !== 'failed').length;

  return (
    <div className="fade-in" style={{ paddingBottom: 48 }}>
      {/* Page header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: '1.65rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 6 }}>
          Campaigns
        </h1>
        <p className="text-sub">Deploy, monitor, and analyze red team operations.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 24, alignItems: 'start' }}>
        {/* ── Left: Deploy form ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card">
            <SectionHeader title="Deploy new campaign" />
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: T.textMuted, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 6 }}>
                  Campaign name
                </label>
                <input className="field" type="text" placeholder="e.g. Lab Scan Alpha"
                  value={name} onChange={e => setName(e.target.value)} required />
              </div>
              <div>
                <label style={{ fontSize: '0.78rem', color: T.textMuted, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 6 }}>
                  Target network
                </label>
                <input className="field" type="text" placeholder="e.g. 192.168.1.0/24"
                  value={target} onChange={e => setTarget(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-red" style={{ marginTop: 4 }}>
                <Plus size={15} /> Create Campaign
              </button>
            </form>
          </div>

          {/* ── Step 2: start ── */}
          {step !== 'idle' && (
            <div className="card fade-in" style={{ borderLeft: `3px solid ${step === 'running' ? T.warning : T.success}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                {step === 'running'
                  ? <span className="dot running" />
                  : <CheckCircle size={14} color={T.success} />}
                <span style={{ fontWeight: 600, fontSize: '0.9rem', color: step === 'running' ? T.warning : T.success }}>
                  {step === 'ready' ? 'Campaign ready' : 'Campaign running'}
                </span>
              </div>
              <p className="text-sub" style={{ marginBottom: 14, fontSize: '0.83rem' }}>
                <strong style={{ color: T.textPrimary }}>{campaignName}</strong> — ID: <span className="mono">{campaignId}</span>
              </p>
              {step === 'ready' && (
                <button className="btn btn-red" onClick={handleStart}>
                  <Zap size={14} /> Launch Operation
                </button>
              )}
              {step === 'running' && (
                <button className="btn btn-ghost" onClick={fetchTasks}>
                  <RefreshCw size={14} /> Refresh tasks
                </button>
              )}
            </div>
          )}

          {/* ── Task stats ── */}
          {tasks.length > 0 && (
            <div className="card fade-in">
              <p style={{ fontSize: '0.78rem', color: T.textMuted, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>Task Summary</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
                {[
                  { label: 'Done',    val: completedCount, color: T.success, dim: T.successDim },
                  { label: 'Pending', val: pendingCount,   color: T.warning, dim: T.warningDim },
                  { label: 'Failed',  val: failedCount,    color: T.danger,  dim: T.dangerDim  },
                ].map(({ label, val, color, dim }) => (
                  <div key={label} style={{ textAlign: 'center', padding: '10px 6px', borderRadius: 8, background: dim }}>
                    <p style={{ fontSize: '1.4rem', fontWeight: 700, color, lineHeight: 1 }}>{val}</p>
                    <p style={{ fontSize: '0.72rem', color, marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Right: Task list ── */}
        <div>
          {!campaignId ? (
            <div className="card">
              <EmptyState icon={Target} message="Create a campaign to see operation tasks here." />
            </div>
          ) : tasks.length === 0 ? (
            <div className="card">
              <EmptyState icon={Clock} message='No tasks yet — click "Launch Operation" to begin.' />
            </div>
          ) : (
            <div className="card">
              <SectionHeader
                title="Operation tasks"
                subtitle={`${tasks.length} tasks · auto-refreshing`}
                action={
                  <button className="btn-icon" onClick={fetchTasks}><RefreshCw size={14} /></button>
                }
              />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 480, overflowY: 'auto', paddingRight: 4 }}>
                {tasks.map(task => (
                  <TaskCard key={task.id} task={task} onAnalyze={handleAnalyzeTask} isAnalyzing={analyzingTask} />
                ))}
              </div>
            </div>
          )}

          {/* ── AI Analysis output ── */}
          {aiAnalysis && (
            <div className="card fade-in" style={{ marginTop: 20, borderLeft: `3px solid ${T.primary}` }}>
              <SectionHeader title="AI task analysis" subtitle="Generated by Ollama local model" />
              <div className="markdown-body" style={{
                background: 'rgba(0,0,0,0.25)', border: `1px solid ${T.border}`,
                borderRadius: 8, padding: '16px 20px',
                color: T.textPrimary, fontSize: '0.875rem', lineHeight: 1.7,
                maxHeight: 360, overflowY: 'auto'
              }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {aiAnalysis}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/* ─── App Root ───────────────────────────────────────────────── */
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());

  return (
    <>
      <GlobalStyles />
      <Router>
        <Routes>
          <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <Login setAuth={setIsAuthenticated} />} />
          <Route path="/" element={isAuthenticated ? <Layout setAuth={setIsAuthenticated}><Dashboard /></Layout> : <Navigate to="/login" />} />
          <Route path="/campaigns" element={isAuthenticated ? <Layout setAuth={setIsAuthenticated}><Campaigns /></Layout> : <Navigate to="/login" />} />
        </Routes>
      </Router>
    </>
  );
};

export default App;
"""

with open("/home/dodo/CRT/redteam-lab/frontend/src/App.jsx", "w") as f:
    f.write(app_code)

print("Updated App.jsx successfully!")

import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Shield, Activity, Users, Target, Grid, MessageSquare, AlertTriangle, FileText, LogOut } from 'lucide-react';
import { setAuthToken } from '../services/api';

const SidebarLink = ({ to, icon: Icon, label }) => (
  <NavLink 
    to={to} 
    className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
  >
    <Icon size={20} />
    <span className="sidebar-link-text">{label}</span>
  </NavLink>
);

const Layout = () => {
  const navigate = useNavigate();
  const [theme, setTheme] = React.useState(localStorage.getItem('theme') || 'dark');

  React.useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('light-mode');
    } else {
      document.body.classList.remove('light-mode');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleLogout = () => {
    setAuthToken(null);
    navigate('/login');
  };

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <Shield size={20} color="white" />
          </div>
          <div>
            <h1 className="sidebar-title">AI-CRT</h1>
            <p className="sidebar-subtitle">Autonomous Agent</p>
          </div>
        </div>

        <nav className="sidebar-nav custom-scrollbar">
          <div className="nav-section-title">Overview</div>
          <SidebarLink to="/dashboard" icon={Activity} label="Dashboard" />
          
          <div className="nav-section-title">Operations</div>
          <SidebarLink to="/campaigns" icon={Target} label="Campaigns" />
          <SidebarLink to="/agents" icon={Users} label="Agents" />
          
          <div className="nav-section-title">Analysis</div>
          <SidebarLink to="/findings" icon={AlertTriangle} label="Findings" />
          <SidebarLink to="/mitre" icon={Grid} label="MITRE Map" />
          <SidebarLink to="/reports" icon={FileText} label="Reports" />
          
          <div className="nav-section-title">Intelligence</div>
          <SidebarLink to="/chat" icon={MessageSquare} label="AI Chat" />
        </nav>

        <div className="sidebar-footer" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <button 
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} 
            className="logout-btn"
            style={{ color: 'var(--text-accent)' }}
          >
            <span className="sidebar-link-text">Toggle Theme</span>
          </button>
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={20} />
            <span className="sidebar-link-text">Disconnect</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content custom-scrollbar">
        {/* Decorative background glow */}
        <div className="main-bg-glow-1" />
        <div className="main-bg-glow-2" />
        
        <div className="main-content-inner">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Campaigns from './pages/Campaigns';
import CampaignDetail from './pages/CampaignDetail';
import MitreMap from './pages/MitreMap';
import AIChat from './pages/AIChat';
import Findings from './pages/Findings';
import Reports from './pages/Reports';

const PlaceholderPage = ({ title }) => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-white mb-2">{title}</h1>
    <p className="text-gray-400">This module is initializing...</p>
  </div>
);

const RequireAuth = ({ children }) => {
  const token = localStorage.getItem('auth_token');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

function App() {
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      import('./services/api').then(({ setAuthToken }) => setAuthToken(token));
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<RequireAuth><Layout /></RequireAuth>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="agents" element={<Agents />} />
          <Route path="campaigns" element={<Campaigns />} />
          <Route path="campaigns/:id" element={<CampaignDetail />} />
          <Route path="findings" element={<Findings />} />
          <Route path="mitre" element={<MitreMap />} />
          <Route path="reports" element={<Reports />} />
          <Route path="chat" element={<AIChat />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

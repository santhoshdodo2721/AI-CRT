import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User as UserIcon, TerminalSquare, AlertTriangle } from 'lucide-react';
import { api, setAuthToken } from '../services/api';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      const res = await api.post('/auth/login', formData);
      setAuthToken(res.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail;
      const errMsg = Array.isArray(detail) ? detail[0].msg : (detail || 'Authentication failed');
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-bg-glow" />
      
      <div className="glass-panel login-card">
        <div className="login-header">
          <div className="login-logo-container">
            <Shield size={32} color="white" />
          </div>
          <h1 className="login-title">AI-CRT Platform</h1>
          <p className="login-subtitle">Autonomous Red Team Operations</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">Operator ID</label>
            <div className="input-icon-wrapper">
              <UserIcon size={18} className="input-icon" />
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="form-input"
                placeholder="Enter username"
                required
              />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Access Key</label>
            <div className="input-icon-wrapper">
              <Lock size={18} className="input-icon" />
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder="Enter password"
                required
              />
            </div>
          </div>

          {error && (
            <div className="error-box">
              <AlertTriangle size={16} className="error-icon" />
              <span>{error}</span>
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="submit-btn"
          >
            {loading ? (
              <div className="loading-spinner" />
            ) : (
              <>
                <TerminalSquare size={18} />
                Access Platform
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;

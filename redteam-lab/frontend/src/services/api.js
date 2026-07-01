import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';
const WS_BASE = 'ws://localhost:8000/ws';

export const api = axios.create({
  baseURL: API_BASE
});

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('auth_token', token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    localStorage.removeItem('auth_token');
  }
};

// Initialize token on load so dashboard doesn't 401 on refresh
const initialToken = localStorage.getItem('auth_token');
if (initialToken) {
  setAuthToken(initialToken);
}

// Intercept 401s to log out
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      setAuthToken(null);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const useCampaignWebsocket = (campaignId) => {
  const [messages, setMessages] = useState([]);
  
  useEffect(() => {
    if (!campaignId) return;
    
    const ws = new WebSocket(`${WS_BASE}?campaign_id=${campaignId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };
    
    return () => {
      ws.close();
    };
  }, [campaignId]);
  
  return messages;
};

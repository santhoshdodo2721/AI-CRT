import axios from 'axios';

// VITE_API_URL should be available in env, fallback to empty string for relative paths
const API_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('redteam_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('redteam_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username, password) => {
    // Note: The FastAPI backend expects form data for login
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    if (response.data.access_token) {
      localStorage.setItem('redteam_token', response.data.access_token);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('redteam_token');
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('redteam_token');
  }
};

export const campaignService = {
  create: async (name, target) => {
    const response = await apiClient.post('/campaigns/', { name, target });
    return response.data;
  },
  start: async (id) => {
    const response = await apiClient.post(`/campaigns/${id}/start`);
    return response.data;
  },
  getAll: async () => {
    const response = await apiClient.get('/campaigns/');
    return response.data || [];
  },
  delete: async (id) => {
    const response = await apiClient.delete(`/campaigns/${id}`);
    return response.data;
  },

  getReport: async (id) => {
    const response = await apiClient.get(`/reports/${id}`);
    return response.data;
  }
};

export const aiService = {
  analyzeTask: async (taskId) => {
    const response = await apiClient.post(`/ai/analyze-task/${taskId}`);
    return response.data;
  },
  generateReport: async (campaignId) => {
    const response = await apiClient.post(`/ai/generate-report/${campaignId}`);
    return response.data;
  }
};

export const taskService = {
  getByCampaign: async (campaignId) => {
    const response = await apiClient.get(`/tasks/campaign/${campaignId}`);
    return response.data;
  },
  getById: async (taskId) => {
    const response = await apiClient.get(`/tasks/${taskId}`);
    return response.data;
  }
};

export const dashboardService = {
  getStats: async () => {
    const response = await apiClient.get('/dashboard/stats');
    return response.data;
  }
};

export const agentService = {
  getAll: async () => {
    const response = await apiClient.get('/agents/');
    return response.data || [];
  }
};

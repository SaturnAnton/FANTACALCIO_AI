import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (email, password) => {
    return apiClient.post('/auth/login', { email, password });
  },
  register: (name, email, password) => {
    return apiClient.post('/auth/signup', { name, email, password });
  },
};

// Predictions API
export const predictionsAPI = {
  getPredictions: (matchday, filters = {}) => {
    return apiClient.get(`/predict/${matchday}`, { params: filters });
  },
  optimizeFormation: (userId, matchday, formation = null) => {
    const params = { matchday };
    if (formation) params.formation = formation;
    return apiClient.get(`/optimize/formation/${userId}`, { params });
  },
  recommendTransfers: (userId, matchday, budget = 0, maxTransfers = 2) => {
    return apiClient.get(`/recommend/transfers/${userId}`, {
      params: { matchday, budget, max_transfers: maxTransfers }
    });
  }
};

// Squad API
export const squadAPI = {
  getSquad: (userId) => {
    return apiClient.get(`/squad/${userId}`);
  },
  addPlayer: (squadId, playerId) => {
    return apiClient.post(`/squad/${squadId}/player`, { player_id: playerId });
  },
  removePlayer: (squadId, playerId) => {
    return apiClient.delete(`/squad/${squadId}/player/${playerId}`);
  }
};

// Players API
export const playersAPI = {
  getPlayers: (filters = {}) => {
    return apiClient.get('/players', { params: filters });
  },
  getPlayerDetails: (playerId) => {
    return apiClient.get(`/players/${playerId}`);
  }
};

export default {
  auth: authAPI,
  predictions: predictionsAPI,
  squad: squadAPI,
  players: playersAPI
};
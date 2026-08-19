import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes for deep LLM analysis
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for unified error parsing and token expiry handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-redirect on login check
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

export const reviewsAPI = {
  createSnippetReview: (data) => api.post('/reviews', data),
  uploadFileReview: (formData) => api.post('/reviews/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getUserReviews: (limit = 50, offset = 0) => api.get(`/reviews?limit=${limit}&offset=${offset}`),
  getReviewById: (id) => api.get(`/reviews/${id}`),
  deleteReview: (id) => api.delete(`/reviews/${id}`),
  getDashboardStats: () => api.get('/reviews/stats/dashboard'),
};

export const githubAPI = {
  analyzeRepo: (data) => api.post('/github/analyze', data),
};

export const projectsAPI = {
  getProjects: () => api.get('/projects'),
  createProject: (data) => api.post('/projects', data),
  getProject: (id) => api.get(`/projects/${id}`),
  deleteProject: (id) => api.delete(`/projects/${id}`),
};

export const healthAPI = {
  getHealth: () => api.get('/health'),
  getOllamaHealth: () => api.get('/health/ollama'),
};

export default api;

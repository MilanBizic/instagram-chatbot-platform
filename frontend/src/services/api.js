 import axios from 'axios';

const api = axios.create({
  baseURL: 'https://instagram-chatbot-platform.onrender.com/api',
  headers: {
    'Content-Type': 'application/json',
  }
});



// Interceptor za dodavanje tokena u svaki request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    console.log('🔑 Sending request with token:', token ? 'YES' : 'NO'); // DEBUG
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 Authorization header:', config.headers.Authorization); // DEBUG
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor za error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.response?.data); // DEBUG
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getMe: () => api.get('/auth/me'),
};

// Chatbot API
export const chatbotAPI = {
  getAll: () => api.get('/chatbots'),
  getById: (id) => api.get(`/chatbots/${id}`),
  create: (data) => api.post('/chatbots', data),
  update: (id, data) => api.put(`/chatbots/${id}`, data),
  delete: (id) => api.delete(`/chatbots/${id}`),
};

// Keyword API
export const keywordAPI = {
  getByBotId: (chatbotId) => api.get(`/chatbots/${chatbotId}/keywords`),
  create: (data) => api.post('/keywords', data),
  update: (id, data) => api.put(`/keywords/${id}`, data),
  delete: (id) => api.delete(`/keywords/${id}`),
};

export default api;
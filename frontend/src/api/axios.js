// src/api/axios.js
import axios from 'axios';

export const api = axios.create({ baseURL: 'http://localhost:8000/api' });

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// DODAJ OVO:
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 403 || error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login'; // Automatski te šalje na login ako token nije validan
    }
    return Promise.reject(error);
  }
);
// src/api.js
import axios from 'axios';

const api = axios.create();

api.interceptors.request.use(config => {
  const token = localStorage.getItem('jwt');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to /unauthorized page on 401/403
api.interceptors.response.use(
  response => response,
  error => {
    const status = error.response?.status;
    if (status === 401 || status === 403) {
      window.location = '/unauthorized';
    }
    return Promise.reject(error);
  }
);

export default api;

import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import apiClient from '../services/apiClient';

const AuthContext = createContext(null);

const basePath = import.meta.env.BASE_URL || '/';

const authApi = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || basePath,
});

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  const setToken = (token) => {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    authApi.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  };

  const clearToken = () => {
    delete apiClient.defaults.headers.common['Authorization'];
    delete authApi.defaults.headers.common['Authorization'];
  };

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      setToken(token);
      authApi.get('api/auth/me')
        .then((res) => setAdmin(res.data))
        .catch(() => {
          localStorage.removeItem('admin_token');
          clearToken();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = (token) => {
    localStorage.setItem('admin_token', token);
    setToken(token);
    return authApi.get('api/auth/me').then((res) => {
      setAdmin(res.data);
      return res.data;
    });
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    clearToken();
    setAdmin(null);
  };

  return (
    <AuthContext.Provider value={{ admin, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

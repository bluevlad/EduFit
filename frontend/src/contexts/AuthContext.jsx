import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import apiClient from '../services/apiClient';

const AuthContext = createContext(null);

// Auth 엔드포인트는 /api/auth prefix (apiClient의 /api/v1 baseURL과 다름)
const baseUrl = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');
const authClient = axios.create({
  baseURL: `${baseUrl}/api`,
  headers: { 'Content-Type': 'application/json' },
});

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  const setToken = (token) => {
    const bearerHeader = `Bearer ${token}`;
    apiClient.defaults.headers.common['Authorization'] = bearerHeader;
    authClient.defaults.headers.common['Authorization'] = bearerHeader;
  };

  const clearToken = () => {
    delete apiClient.defaults.headers.common['Authorization'];
    delete authClient.defaults.headers.common['Authorization'];
  };

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      setToken(token);
      authClient.get('/auth/me')
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

  const verifyGoogleToken = async (credential) => {
    const res = await authClient.post('/auth/google/verify', { credential });
    const { access_token, user } = res.data;
    localStorage.setItem('admin_token', access_token);
    setToken(access_token);
    setAdmin(user);
    return { user };
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    clearToken();
    setAdmin(null);
  };

  return (
    <AuthContext.Provider value={{ admin, loading, verifyGoogleToken, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

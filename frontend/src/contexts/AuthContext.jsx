import { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  const setToken = (token) => {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  };

  const clearToken = () => {
    delete apiClient.defaults.headers.common['Authorization'];
  };

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      setToken(token);
      apiClient.get('/api/auth/me')
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
    const res = await apiClient.post('/api/auth/google/verify', { credential });
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

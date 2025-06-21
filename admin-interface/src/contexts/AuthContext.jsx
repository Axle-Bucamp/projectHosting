import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('admin_token'));
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!token && !!user;

  const API_BASE_URL = import.meta?.env?.VITE_API_URL || 'http://localhost:8000';; 

  const verifyToken = useCallback(async (savedToken) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/dashboard`, {
        headers: {
          Authorization: `Bearer ${savedToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user || { username: 'admin', role: 'admin' }); // Fallback user
        return true;
      } else {
        throw new Error('Invalid token');
      }
    } catch (err) {
      console.error('Auth verification failed:', err);
      localStorage.removeItem('admin_token');
      setToken(null);
      setUser(null);
      return false;
    }
  }, [API_BASE_URL]);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('admin_token');
      if (savedToken) {
        setToken(savedToken);
        await verifyToken(savedToken);
      }
      setLoading(false);
    };
    initAuth();
  }, [verifyToken]);

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok && data.success && data.token) {
        localStorage.setItem('admin_token', data.token);
        setToken(data.token);
        setUser(data.user || { username });
        return { success: true };
      }

      return { success: false, error: data.error || 'Login failed' };
    } catch (err) {
      console.error('Login error:', err);
      return { success: false, error: 'Network error' };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('admin_token');
  };

  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

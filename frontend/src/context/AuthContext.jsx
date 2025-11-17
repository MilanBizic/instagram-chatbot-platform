import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    console.log('Token from storage:', token); // DEBUG
    
    if (token) {
      try {
        const response = await authAPI.getMe();
        console.log('User data:', response.data); // DEBUG
        setUser(response.data);
      } catch (error) {
        console.error('Auth check failed:', error); // DEBUG
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      console.log('Login response:', response.data); // DEBUG
      
      const { access_token } = response.data;
      console.log('Access token:', access_token); // DEBUG
      
      if (!access_token) {
        throw new Error('No access token received');
      }
      
      localStorage.setItem('token', access_token);
      console.log('Token saved to storage'); // DEBUG
      
      await checkAuth();
      return response;
    } catch (error) {
      console.error('Login error:', error); // DEBUG
      throw error;
    }
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    return response;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
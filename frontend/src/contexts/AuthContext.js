import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Export AuthContext so it can be imported in other components
export const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      setAuthToken(token);
      setIsAuthenticated(true);
      
      // Get user data
      const userData = localStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    }
    setLoading(false);
  }, []);

  // Set auth token in axios headers
  const setAuthToken = (token) => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  // Register user
  const register = async (name, email, password) => {
    try {
      setError(null);
      const res = await axios.post(`${API_URL}/auth/signup`, {
        name,
        email,
        password
      });
      
      // Login after successful registration
      await login(email, password);
      
      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      throw err;
    }
  };

  // Login user
  const login = async (email, password) => {
    try {
      setError(null);
      const res = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      });
      
      const { access_token, user: userData } = res.data;
      
      // Save token and user data
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Set auth token in headers
      setAuthToken(access_token);
      
      // Update state
      setUser(userData);
      setIsAuthenticated(true);
      
      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    }
  };

  // Logout user
  const logout = () => {
    // Remove token and user data
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Remove auth token from headers
    setAuthToken(null);
    
    // Update state
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        error,
        register,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
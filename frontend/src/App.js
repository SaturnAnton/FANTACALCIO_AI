import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Squad from './pages/Squad';
import Predictions from './pages/Predictions';
import Lineup from './pages/Lineup';
import Trades from './pages/Trades';
import Navbar from './components/Navbar';
import './App.css';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <div className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/squad" element={
                <ProtectedRoute>
                  <Squad />
                </ProtectedRoute>
              } />
              <Route path="/predictions" element={
                <ProtectedRoute>
                  <Predictions />
                </ProtectedRoute>
              } />
              <Route path="/lineup" element={
                <ProtectedRoute>
                  <Lineup />
                </ProtectedRoute>
              } />
              <Route path="/trades" element={
                <ProtectedRoute>
                  <Trades />
                </ProtectedRoute>
              } />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
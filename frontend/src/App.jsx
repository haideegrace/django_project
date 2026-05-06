/**
 * Main App Component
 * Root component for the React frontend
 * Handles authentication state and page routing
 */

import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { Dashboard } from './components/Dashboard';
import { Animals } from './components/Animals';
import { EggProduction } from './components/EggProduction';
import { Login } from './components/Login';
import { authAPI, clearAuth, getStoredUser, isAuthenticated } from './services/apiService';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [user, setUser] = useState(getStoredUser());
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(isAuthenticated());
  const [loggingOut, setLoggingOut] = useState(false);

  // Listen for auth-expired events (e.g., 401 from API interceptor)
  useEffect(() => {
    const handleAuthExpired = () => {
      setIsLoggedIn(false);
      setUser(null);
    };

    window.addEventListener('auth-expired', handleAuthExpired);
    return () => window.removeEventListener('auth-expired', handleAuthExpired);
  }, []);

  // Verify token is still valid on mount
  useEffect(() => {
    if (isLoggedIn) {
      authAPI.getCurrentUser()
        .then((response) => {
          setUser(response.data);
        })
        .catch(() => {
          // Token is invalid
          clearAuth();
          setIsLoggedIn(false);
          setUser(null);
        });
    }
  }, [isLoggedIn]);

  const handleLoginSuccess = useCallback((userData) => {
    setUser(userData);
    setIsLoggedIn(true);
    setCurrentPage('dashboard');
  }, []);

  const handleLogout = useCallback(async () => {
    setLoggingOut(true);
    try {
      await authAPI.logout();
    } catch (err) {
      // Even if API call fails, clear local auth
      console.warn('Logout API call failed:', err);
    } finally {
      clearAuth();
      setUser(null);
      setIsLoggedIn(false);
      setCurrentPage('dashboard');
      setLoggingOut(false);
    }
  }, []);

  // Show login page if not authenticated
  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'animals':
        return <Animals />;
      case 'egg-production':
        return <EggProduction />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <button
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <h1 className="app-title">🌾 Farm Management System</h1>
          <div className="user-section">
            {user && <span className="user-name">👤 {user.username}</span>}
            <button
              className="logout-btn"
              onClick={handleLogout}
              disabled={loggingOut}
            >
              {loggingOut ? 'Logging out...' : 'Logout'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="app-container">
        {/* Sidebar Navigation */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <nav className="sidebar-nav">
            <button
              className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              className={`nav-item ${currentPage === 'animals' ? 'active' : ''}`}
              onClick={() => setCurrentPage('animals')}
            >
              🐔 Animals
            </button>
            <button
              className={`nav-item ${currentPage === 'egg-production' ? 'active' : ''}`}
              onClick={() => setCurrentPage('egg-production')}
            >
              🥚 Egg Production
            </button>
            <hr />
            <p className="nav-label">More Features Coming Soon</p>
            <button className="nav-item disabled">
              🌾 Feed Inventory
            </button>
            <button className="nav-item disabled">
              ⚠️ Mortality Records
            </button>
            <button className="nav-item disabled">
              👥 Employees
            </button>
            <button className="nav-item disabled">
              📈 Reports
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <div className="page-container">
            {renderPage()}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <p>© 2024 Farm Management System. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;

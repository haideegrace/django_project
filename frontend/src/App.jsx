/**
 * Main App Component
 * Root component for the React frontend
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import { Dashboard } from './components/Dashboard';
import { Animals } from './components/Animals';
import { EggProduction } from './components/EggProduction';
import { Login } from './components/Login';
import { getAuth, clearAuth } from './services/apiService';
import webSocketService from './services/webSocketService';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const { token, user: savedUser } = getAuth();
    if (token && savedUser) {
      setUser(savedUser);
    }
  }, []);

  const handleLoginSuccess = (loggedInUser) => {
    setUser(loggedInUser);
  };

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    setCurrentPage('dashboard');
  };

  // If not logged in, show login page
  if (!user) {
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
            {user && <span className="user-name">{user.username}</span>}
            <button onClick={handleLogout} className="logout-link">Logout</button>
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


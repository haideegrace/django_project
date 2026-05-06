/**
 * Dashboard Component - Main dashboard showing real-time data
 */

import React, { useEffect, useState } from 'react';
import { useDashboardRealtime } from '../hooks';
import { dashboardAPI } from '../services/apiService';
import './Dashboard.css';

export const Dashboard = () => {
  const { dashboardData, alerts, activities, isConnected, requestUpdate } = useDashboardRealtime();
  const [staticData, setStaticData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch initial data if WebSocket doesn't provide it
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const data = await dashboardAPI.getSummary();
        setStaticData(data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  const data = dashboardData || staticData;

  if (loading && !data) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Farm Dashboard</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
          {isConnected ? 'Live Updates' : 'Offline'}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-grid">
        <SummaryCard
          icon="🐔"
          title="Total Animals"
          value={data?.total_animals || 0}
          detail="Flock size"
        />
        <SummaryCard
          icon="🥚"
          title="Today's Eggs"
          value={data?.total_eggs_today || 0}
          detail={`Weekly: ${data?.total_eggs_week || 0}`}
        />
        <SummaryCard
          icon="🌾"
          title="Feed Stock"
          value={`${data?.total_feed_stock?.toFixed(1) || 0} kg`}
          detail={data?.feed_status === 'critical' ? '⚠️ Critical' : data?.feed_status === 'warning' ? '⚠️ Low' : '✓ Stable'}
          status={data?.feed_status}
        />
        <SummaryCard
          icon="📋"
          title="Recent Mortality"
          value={data?.recent_mortality || 0}
          detail="Last 7 days"
        />
      </div>

      {/* Alerts Section */}
      {alerts && alerts.length > 0 && (
        <div className="alerts-section">
          <h3>🚨 Active Alerts</h3>
          <div className="alerts-list">
            {alerts.slice(0, 5).map((alert, index) => (
              <div key={index} className={`alert alert-${alert.severity || 'info'}`}>
                <strong>{alert.title}</strong>
                <p>{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {activities && activities.length > 0 && (
        <div className="activity-section">
          <h3>📋 Recent Activity</h3>
          <div className="activity-list">
            {activities.slice(0, 10).map((activity) => (
              <div key={activity.id} className="activity-item">
                <div className="activity-time">{activity.time}</div>
                <div className="activity-content">
                  <strong>{activity.employee_name}</strong> - {activity.activity_type_display}
                  {activity.animal_name && <span> on {activity.animal_name}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analytics Section */}
      {data?.analytics && (
        <div className="analytics-section">
          <h3>📈 Analytics</h3>
          <div className="analytics-grid">
            {Object.entries(data.analytics).map(([key, value]) => (
              <div key={key} className="analytics-item">
                <strong>{key.replace(/_/g, ' ')}</strong>
                <p>{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <button
        className="btn-refresh"
        onClick={() => requestUpdate('get_dashboard')}
        disabled={!isConnected}
      >
        🔄 Refresh
      </button>
    </div>
  );
};

/**
 * Summary Card Component
 */
const SummaryCard = ({ icon, title, value, detail, status }) => {
  return (
    <div className={`summary-card ${status ? `status-${status}` : ''}`}>
      <div className="card-icon">{icon}</div>
      <div className="card-title">{title}</div>
      <div className="card-value">{value}</div>
      <div className="card-detail">{detail}</div>
    </div>
  );
};

export default Dashboard;

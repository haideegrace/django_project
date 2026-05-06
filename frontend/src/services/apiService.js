/**
 * API Service for communicating with Django REST Backend
 * Handles all HTTP requests and responses
 * Uses Token-based authentication for cross-domain support (Vercel → Render)
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===== TOKEN MANAGEMENT =====

/**
 * Attach auth token to every request automatically
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Handle 401 responses globally — redirect to login
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token is invalid or expired — clear it
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      // Trigger a custom event so App.jsx can react
      window.dispatchEvent(new Event('auth-expired'));
    }
    return Promise.reject(error);
  }
);

// ===== AUTH ENDPOINTS =====

export const authAPI = {
  login: (username, password) =>
    apiClient.post('/auth/login/', { username, password }),

  logout: () =>
    apiClient.post('/auth/logout/'),

  getCurrentUser: () =>
    apiClient.get('/auth/user/'),
};

/**
 * Helper: Save auth data to localStorage
 */
export const saveAuth = (token, user) => {
  localStorage.setItem('authToken', token);
  localStorage.setItem('user', JSON.stringify(user));
};

/**
 * Helper: Clear auth data from localStorage
 */
export const clearAuth = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
};

/**
 * Helper: Get stored user
 */
export const getStoredUser = () => {
  try {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
};

/**
 * Helper: Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('authToken');
};


// ===== ANIMALS ENDPOINTS =====

export const animalAPI = {
  getAll: () => apiClient.get('/animals/'),
  getById: (id) => apiClient.get(`/animals/${id}/`),
  create: (data) => apiClient.post('/animals/', data),
  update: (id, data) => apiClient.put(`/animals/${id}/`, data),
  delete: (id) => apiClient.delete(`/animals/${id}/`),
  getByCategory: (category) => apiClient.get('/animals/by_category/', { params: { category } }),
  getStatistics: (id) => apiClient.get(`/animals/${id}/statistics/`),
};

/**
 * EGG PRODUCTION ENDPOINTS
 */
export const eggProductionAPI = {
  getAll: () => apiClient.get('/egg-production/'),
  getById: (id) => apiClient.get(`/egg-production/${id}/`),
  create: (data) => apiClient.post('/egg-production/', data),
  update: (id, data) => apiClient.put(`/egg-production/${id}/`, data),
  delete: (id) => apiClient.delete(`/egg-production/${id}/`),
  getByDateRange: (startDate, endDate) =>
    apiClient.get('/egg-production/by_date_range/', {
      params: { start_date: startDate, end_date: endDate },
    }),
  getTodayTotal: () => apiClient.get('/egg-production/today_total/'),
  getWeeklySummary: () => apiClient.get('/egg-production/weekly_summary/'),
};

/**
 * FEED ENDPOINTS
 */
export const feedAPI = {
  getAll: () => apiClient.get('/feeds/'),
  getById: (id) => apiClient.get(`/feeds/${id}/`),
  create: (data) => apiClient.post('/feeds/', data),
  update: (id, data) => apiClient.put(`/feeds/${id}/`, data),
  delete: (id) => apiClient.delete(`/feeds/${id}/`),
  getLowStock: () => apiClient.get('/feeds/low_stock/'),
  getStockSummary: () => apiClient.get('/feeds/stock_summary/'),
};

/**
 * FEED USAGE ENDPOINTS
 */
export const feedUsageAPI = {
  getAll: () => apiClient.get('/feed-usage/'),
  getById: (id) => apiClient.get(`/feed-usage/${id}/`),
  create: (data) => apiClient.post('/feed-usage/', data),
  update: (id, data) => apiClient.put(`/feed-usage/${id}/`, data),
  delete: (id) => apiClient.delete(`/feed-usage/${id}/`),
  getByDateRange: (startDate, endDate) =>
    apiClient.get('/feed-usage/by_date_range/', {
      params: { start_date: startDate, end_date: endDate },
    }),
};

/**
 * MORTALITY ENDPOINTS
 */
export const mortalityAPI = {
  getAll: () => apiClient.get('/mortality/'),
  getById: (id) => apiClient.get(`/mortality/${id}/`),
  create: (data) => apiClient.post('/mortality/', data),
  update: (id, data) => apiClient.put(`/mortality/${id}/`, data),
  delete: (id) => apiClient.delete(`/mortality/${id}/`),
  getByDateRange: (startDate, endDate) =>
    apiClient.get('/mortality/by_date_range/', {
      params: { start_date: startDate, end_date: endDate },
    }),
  getWeeklySummary: () => apiClient.get('/mortality/weekly_summary/'),
};

/**
 * ACTIVITY LOG ENDPOINTS
 */
export const activityAPI = {
  getAll: () => apiClient.get('/activities/'),
  getById: (id) => apiClient.get(`/activities/${id}/`),
  getToday: () => apiClient.get('/activities/today/'),
  getByDateRange: (startDate, endDate, activityType = null) => {
    const params = { start_date: startDate, end_date: endDate };
    if (activityType) params.activity_type = activityType;
    return apiClient.get('/activities/by_date_range/', { params });
  },
};

/**
 * EMPLOYEE ENDPOINTS
 */
export const employeeAPI = {
  getAll: () => apiClient.get('/employees/'),
  getById: (id) => apiClient.get(`/employees/${id}/`),
};

/**
 * NOTIFICATION ENDPOINTS
 */
export const notificationAPI = {
  getAll: () => apiClient.get('/notifications/'),
  getById: (id) => apiClient.get(`/notifications/${id}/`),
  markAsRead: (id) => apiClient.post(`/notifications/${id}/mark_as_read/`),
  markAllAsRead: () => apiClient.post('/notifications/mark_all_as_read/'),
  clearAll: () => apiClient.post('/notifications/clear_all/'),
  getUnreadCount: () => apiClient.get('/notifications/unread_count/'),
};

/**
 * USER PROFILE ENDPOINTS
 */
export const profileAPI = {
  getMe: () => apiClient.get('/profile/me/'),
  updateProfile: (data) => apiClient.put('/profile/update_profile/', data),
};

/**
 * DASHBOARD ENDPOINTS
 */
export const dashboardAPI = {
  getSummary: () => apiClient.get('/dashboard/summary/'),
  getRecentActivity: () => apiClient.get('/dashboard/recent_activity/'),
};

/**
 * Error handler for API responses
 */
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    return {
      status: error.response.status,
      message: error.response.data.detail || error.response.data.error || 'An error occurred',
      data: error.response.data,
    };
  } else if (error.request) {
    // Request was made but no response
    return {
      status: 0,
      message: 'No response from server. Check your connection.',
      data: null,
    };
  }
  // Error in request setup
  return {
    status: 0,
    message: error.message,
    data: null,
  };
};

export default apiClient;

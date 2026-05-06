/**
 * Custom React Hooks for Farm Management App
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient, { handleAPIError } from '../services/apiService';
import webSocketService from '../services/webSocketService';

/**
 * Hook for fetching data from API with automatic error handling and loading states
 */
export const useFetch = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get(url, options);
      setData(response.data);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch };
};

/**
 * Hook for real-time dashboard updates via WebSocket
 */
export const useDashboardRealtime = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [activities, setActivities] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const unsubscribeRef = useRef(null);

  useEffect(() => {
    const initializeWebSocket = async () => {
      try {
        await webSocketService.connect('/dashboard/');
        setIsConnected(true);

        // Request initial dashboard data
        webSocketService.send({ command: 'get_dashboard' });

        // Listen for dashboard updates
        unsubscribeRef.current = webSocketService.on('dashboard_update', (message) => {
          setDashboardData(message.data);
        });

        // Listen for activities updates
        webSocketService.on('activities_update', (message) => {
          setActivities(message.data);
        });

        // Listen for alerts
        webSocketService.on('alerts_update', (message) => {
          setAlerts(message.data);
        });

        // Listen for activity created
        webSocketService.on('activity_created', (message) => {
          setActivities(prev => [message.data, ...prev].slice(0, 10));
        });

        // Listen for egg production recorded
        webSocketService.on('egg_production_recorded', (message) => {
          setDashboardData(prev => {
            if (!prev) return prev;
            return {
              ...prev,
              total_eggs_today: prev.total_eggs_today + (message.data.quantity || 0)
            };
          });
        });

        // Listen for mortality recorded
        webSocketService.on('mortality_recorded', (message) => {
          setDashboardData(prev => {
            if (!prev) return prev;
            return {
              ...prev,
              recent_mortality: prev.recent_mortality + (message.data.count || 0)
            };
          });
        });

        // Listen for feed alerts
        webSocketService.on('feed_alert', (message) => {
          setAlerts(prev => [message.data, ...prev]);
        });

      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        setIsConnected(false);
      }
    };

    initializeWebSocket();

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      // Keep connection alive but clean up listeners
    };
  }, []);

  const requestUpdate = useCallback((command) => {
    if (isConnected) {
      webSocketService.send({ command });
    }
  }, [isConnected]);

  return {
    dashboardData,
    alerts,
    activities,
    isConnected,
    requestUpdate,
  };
};

/**
 * Hook for real-time notifications via WebSocket
 */
export const useNotificationsRealtime = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const initializeWebSocket = async () => {
      try {
        await webSocketService.connect('/notifications/');
        setIsConnected(true);

        // Listen for new notifications
        webSocketService.on('notification', (message) => {
          const newNotification = {
            id: message.id,
            title: message.title,
            message: message.message,
            type: message.notification_type,
            timestamp: message.timestamp,
          };
          
          setNotifications(prev => [newNotification, ...prev]);
          setUnreadCount(prev => prev + 1);
        });

      } catch (error) {
        console.error('Failed to connect to notifications WebSocket:', error);
        setIsConnected(false);
      }
    };

    initializeWebSocket();

    return () => {
      // Connection stays alive
    };
  }, []);

  return {
    notifications,
    unreadCount,
    isConnected,
  };
};

/**
 * Hook for posting data with error handling
 */
export const usePost = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const post = useCallback(async (url, data) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.post(url, data);
      return response.data;
    } catch (err) {
      const errorInfo = handleAPIError(err);
      setError(errorInfo);
      throw errorInfo;
    } finally {
      setLoading(false);
    }
  }, []);

  return { post, loading, error };
};

/**
 * Hook for polling data at intervals
 */
export const usePoll = (fetchFunction, interval = 5000, enabled = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const poll = useCallback(async () => {
    try {
      setLoading(true);
      const result = await fetchFunction();
      setData(result);
      setError(null);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  }, [fetchFunction]);

  useEffect(() => {
    if (!enabled) return;

    // Initial fetch
    poll();

    // Set up polling interval
    intervalRef.current = setInterval(poll, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [poll, interval, enabled]);

  return { data, loading, error };
};

/**
 * Hook for debounced search
 */
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Hook for form handling
 */
export const useForm = (initialValues, onSubmit) => {
  const [values, setValues] = useState(initialValues);
  const [touched, setTouched] = useState({});
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((event) => {
    const { name, value, type, checked } = event.target;
    setValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }, []);

  const handleBlur = useCallback((event) => {
    const { name } = event.target;
    setTouched(prev => ({
      ...prev,
      [name]: true,
    }));
  }, []);

  const handleSubmit = useCallback(async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (err) {
      setErrors(err.data || {});
    } finally {
      setIsSubmitting(false);
    }
  }, [values, onSubmit]);

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setTouched({});
    setErrors({});
  }, [initialValues]);

  return {
    values,
    touched,
    errors,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setValues,
  };
};

/**
 * Hook for managing async state with cache
 */
export const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const cacheRef = useRef({});

  const execute = useCallback(
    async (...args) => {
      const cacheKey = JSON.stringify(args);
      
      if (cacheRef.current[cacheKey]) {
        setData(cacheRef.current[cacheKey]);
        return cacheRef.current[cacheKey];
      }

      setStatus('pending');
      setData(null);
      setError(null);

      try {
        const result = await asyncFunction(...args);
        cacheRef.current[cacheKey] = result;
        setData(result);
        setStatus('success');
        return result;
      } catch (err) {
        setError(err);
        setStatus('error');
        throw err;
      }
    },
    [asyncFunction]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { execute, status, data, error };
};

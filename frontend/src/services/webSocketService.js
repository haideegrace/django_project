/**
 * WebSocket Service for Real-time Updates
 * Handles WebSocket connections and message handling
 */

const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.isManualClose = false;
  }

  /**
   * Connect to WebSocket
   */
  connect(endpoint) {
    return new Promise((resolve, reject) => {
      try {
        const url = `${WS_BASE_URL}${endpoint}`;
        console.log('Connecting to WebSocket:', url);
        
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.emit('connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);
            
            // Emit event based on message type
            if (data.type) {
              this.emit(data.type, data);
            }
            
            // Also emit a generic 'message' event
            this.emit('message', data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.emit('error', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.emit('disconnected');
          
          // Attempt to reconnect
          if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connect(endpoint), this.reconnectDelay);
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Send message through WebSocket
   */
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  /**
   * Register event listener
   */
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
    
    // Return unsubscribe function
    return () => this.off(event, callback);
  }

  /**
   * Unregister event listener
   */
  off(event, callback) {
    if (!this.listeners[event]) return;
    
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }

  /**
   * Emit event to all listeners
   */
  emit(event, data) {
    if (!this.listeners[event]) return;
    
    this.listeners[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in listener for ${event}:`, error);
      }
    });
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    this.isManualClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;

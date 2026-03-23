

// import io from 'socket.io-client';
// import { payway_socket_server_url } from "../../../../../sites/common_site_config.json" 
// let payway_socket = io(payway_socket_server_url, { path: '/estc-socket-server/socket.io' });
// export default payway_socket;

// utils/paywaysocketio.js
import io from 'socket.io-client';

class PaywaySocket {
  constructor(serverUrl) {
    if (!serverUrl) {
      throw new Error('Server URL is required');
    }
    
    this.serverUrl = serverUrl;
    this.socket = null;
    this.isConnected = false;
    this.rooms = new Set();
    
    this.initializeSocket();
  }
  
  initializeSocket() {
    this.socket = io(this.serverUrl, {
      path: '/estc-socket-server/socket.io',
      transports: ['websocket', 'polling'],
      autoConnect: true, // Auto connect when instance is created
      reconnection: true,
      // reconnectionAttempts: 5,
      // reconnectionDelay: 1000,
    });
    
    this.setupDefaultListeners();
  }
  
  setupDefaultListeners() {
    this.socket.on('connect', () => {
      this.isConnected = true;
      console.log('PaywaySocket connected:', this.socket.id);
      
      // Re-join rooms on reconnect
      this.rooms.forEach(room => {
        this.socket.emit('joinRoom', room);
      });
    });
    
    this.socket.on('disconnect', (reason) => {
      this.isConnected = false;
      console.log('PaywaySocket disconnected:', reason);
    });
  }
  
  // Join a room
  joinRoom(roomName) {
    if (this.socket && roomName) {
      this.socket.emit('joinRoom', roomName);
      this.rooms.add(roomName);
    }
    return this;
  }
  
  // Leave a room
  leaveRoom(roomName) {
    if (this.socket && roomName) {
      this.socket.emit('leaveRoom', roomName);
      this.rooms.delete(roomName);
    }
    return this;
  }
  
  // Emit event
  emit(event, data) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
    return this;
  }
  
  // Listen to event
  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
    return this;
  }
  
  // Remove listener
  off(event, callback) {
    if (this.socket) {
      if (callback) {
        this.socket.off(event, callback);
      } else {
        this.socket.off(event);
      }
    }
    return this;
  }
  
  // Disconnect
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.rooms.clear();
    }
    return this;
  }
  
  // Get connection status
  getIsConnected() {
    return this.isConnected;
  }
  
  // Get socket ID
  getId() {
    return this.socket ? this.socket.id : null;
  }
}

// Factory function
export default function createPaywaySocket(serverUrl) {
  return new PaywaySocket(serverUrl);
}

// Also export class for direct usage if needed
// export { PaywaySocket };
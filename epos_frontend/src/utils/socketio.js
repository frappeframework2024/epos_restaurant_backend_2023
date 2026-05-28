import io from 'socket.io-client';

const socket = io(window.location.origin, {
    path: '/socketserver/socket.io',
    transports: ['websocket', 'polling']
});

export default socket;
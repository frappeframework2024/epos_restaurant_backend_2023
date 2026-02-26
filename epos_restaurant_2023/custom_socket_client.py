import socketio

# Point this to your Node.js Socket.IO server
SOCKET_SERVER_URL = "http://localhost:3000"
sio = socketio.Client()

def connect_socket():
    if not sio.connected:
        try:
            sio.connect(SOCKET_SERVER_URL, socketio_path="socketserver/socket.io")
            print("✅ Connected to Socket.IO server")
        except Exception as e:
            print("❌ Socket.IO connection failed:", e)

def emit_event(event, data):
    try:
        connect_socket()
        sio.emit(event, data)
        print(f"📤 Event sent: {event} => {data}")
    except Exception as e:
        print("❌ Emit failed:", e)

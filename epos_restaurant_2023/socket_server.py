import socket
import threading
import frappe

class TCPSocketServer:
    def __init__(self, host='0.0.0.0', port=4040):
        """Initialize the TCP socket server."""
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.client_threads = []
        frappe.logger().info(f"TCPSocketServer initialized with host={host}, port={port}")

    def socket_handler(self, client_socket, address):
        """Handle individual client connections."""
        frappe.logger().info(f"Client connected from {address}")
        print(f"Client connected: {address}")  # Debug to console
        try:
            # Send welcome message to client
            welcome_msg = "Connected to ePOS Restaurant TCP Server\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            while self.running:
                # Receive data from client
                data = client_socket.recv(1024)
                if not data:
                    break  # Client disconnected
                try:
                    decoded_data = data.decode('utf-8').strip()
                    frappe.logger().info(f"Received from {address}: {decoded_data}")
                    print(f"Received from {address}: {decoded_data}")  # Debug
                    # Echo back with timestamp
                    response = f"Echo: {decoded_data} - {frappe.utils.now()}\n"
                    client_socket.send(response.encode('utf-8'))
                except UnicodeDecodeError:
                    frappe.logger().error(f"Invalid UTF-8 data from {address}")
                    client_socket.send("Error: Invalid data format\n".encode('utf-8'))
        except Exception as e:
            frappe.logger().error(f"Error with client {address}: {e}")
            print(f"Client error {address}: {e}")  # Debug
        finally:
            frappe.logger().info(f"Client disconnected: {address}")
            print(f"Client disconnected: {address}")  # Debug
            client_socket.close()

    def start(self):
        """Start the TCP server and listen for connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            # Bind to host and port
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)  # Allow up to 5 queued connections
            self.running = True
            frappe.logger().info(f"TCP Socket Server successfully started on {self.host}:{self.port}")
            print(f"TCP Socket Server started on {self.host}:{self.port}")  # Debug
        except Exception as e:
            frappe.logger().error(f"Failed to bind to {self.host}:{self.port}: {e}")
            print(f"Bind error: {e}")  # Debug
            self.running = False
            return

        # Accept client connections
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                frappe.logger().info(f"Accepted connection from {address}")
                print(f"Accepted connection from {address}")  # Debug
                # Start a thread for each client
                client_thread = threading.Thread(target=self.socket_handler, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
                self.client_threads.append(client_thread)
            except Exception as e:
                if self.running:  # Log only if not intentionally stopped
                    frappe.logger().error(f"Accept error: {e}")
                    print(f"Accept error: {e}")  # Debug

    def stop(self):
        """Stop the server and clean up."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            frappe.logger().info("Server socket closed")
            print("Server socket closed")  # Debug
        # Wait for client threads to finish
        for thread in self.client_threads:
            thread.join(timeout=1.0)
        frappe.logger().info("TCP Socket Server stopped")
        print("TCP Socket Server stopped")  # Debug

    def run(self):
        """Run the server in a background thread."""
        socket_thread = threading.Thread(target=self.start, daemon=True)
        socket_thread.start()
        frappe.logger().info("TCP Socket Server thread started")
        print("TCP Socket Server thread started")  # Debug
        return self

# Global instance
socket_server = None

def start_socket_server():
    """Start the socket server if not already running."""
    global socket_server
    if not socket_server:
        host = frappe.conf.get("socket_server_host", "0.0.0.0")
        port = frappe.conf.get("socket_server_port", 4040)
        frappe.logger().info(f"Starting socket server on {host}:{port}")
        print(f"Starting socket server on {host}:{port}")  # Debug
        socket_server = TCPSocketServer(host=host, port=port)
        socket_server.run()

def stop_socket_server():
    """Stop the socket server if running."""
    global socket_server
    if socket_server:
        socket_server.stop()
        socket_server = None
        frappe.logger().info("Socket server stopped via stop_socket_server")
        print("Socket server stopped via stop_socket_server")  # Debug

# Optional: Test standalone (uncomment to run outside Frappe for debugging)
# if __name__ == "__main__":
#     server = TCPSocketServer()
#     server.run()
#     import time
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         server.stop()
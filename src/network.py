import socket
import threading
import json
import time
from typing import Optional, Dict, Any, Callable
from enum import Enum
import ipaddress

class NetworkMessageType(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GAME_START = "game_start"
    PLAYER_READY = "player_ready"
    PLAYER_CHOICE = "player_choice"
    GAME_RESULT = "game_result"
    CHAT_MESSAGE = "chat_message"
    ERROR = "error"

class NetworkManager:
    def __init__(self, host: str = "0.0.0.0", port: int = 5555):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.room_code: Optional[str] = None
        self.player_id: Optional[str] = None
        self.opponent_name: Optional[str] = None
        self.message_handlers: Dict[NetworkMessageType, Callable[[Dict[str, Any]], None]] = {}
        self.receive_thread: Optional[threading.Thread] = None
        self.buffer_size = 4096
        self.client_socket: Optional[socket.socket] = None
        self.is_server = False
        self.local_ip = self._get_local_ip()
    
    def _get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            # Create a socket to find the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def set_message_handler(self, message_type: NetworkMessageType, handler: Callable[[Dict[str, Any]], None]):
        """Set a handler for a specific message type"""
        self.message_handlers[message_type] = handler
    
    def start_server(self, port: int = 5555) -> Optional[str]:
        """Start the game server and return room code"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, port))
            self.socket.listen(1)
            self.connected = True
            self.is_server = True
            self.port = port
            
            # Generate room code from IP and port
            self.room_code = f"{self.local_ip}:{port}"
            
            # Start listening for connections in a separate thread
            self.receive_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.receive_thread.start()
            
            print(f"Server started on {self.local_ip}:{port}")
            return self.room_code
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return None
    
    def connect_to_server(self, host: str, port: int) -> bool:
        """Connect to a game server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            self.is_server = False
            
            # Start receiving messages in a separate thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            print(f"Connected to server at {host}:{port}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.connected = False
            return False
    
    def _accept_connections(self):
        """Accept incoming connections (server only)"""
        while self.connected and self.socket:
            try:
                client_socket, address = self.socket.accept()
                print(f"New connection from {address}")
                self.client_socket = client_socket
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.connected:  # Only print if we didn't close the socket intentionally
                    print(f"Error accepting connection: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle a connected client (server only)"""
        buffer = ""
        try:
            while self.connected:
                data = client_socket.recv(self.buffer_size)
                if not data:
                    break
                
                # Accumulate data in buffer
                buffer += data.decode('utf-8')
                
                # Process complete messages (separated by newlines)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message.strip():
                        self._process_message(message, client_socket)
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
    
    def _receive_messages(self):
        """Receive messages from the server (client only)"""
        buffer = ""
        while self.connected and self.socket:
            try:
                data = self.socket.recv(self.buffer_size)
                if not data:
                    break
                
                # Accumulate data in buffer
                buffer += data.decode('utf-8')
                
                # Process complete messages (separated by newlines)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message.strip():
                        self._process_message(message)
                    
            except Exception as e:
                if self.connected:  # Only print if we didn't close the socket intentionally
                    print(f"Error receiving message: {e}")
                break
    
    def _process_message(self, message: str, client_socket: socket.socket = None):
        """Process a received message"""
        try:
            message_data = json.loads(message)
            message_type = NetworkMessageType(message_data.get("type"))
            
            # Call the appropriate handler if registered
            if message_type in self.message_handlers:
                self.message_handlers[message_type](message_data)
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Invalid message format: {e}")
    
    def send_message(self, message_type: NetworkMessageType, data: Optional[Dict[str, Any]] = None) -> bool:
        """Send a message to the connected peer"""
        if not self.connected:
            return False
            
        try:
            message = {
                "type": message_type.value,
                "timestamp": time.time(),
                "data": data or {}
            }
            
            serialized = json.dumps(message) + "\n"
            
            # Send to appropriate socket
            target_socket = self.client_socket if self.is_server and self.client_socket else self.socket
            
            if target_socket:
                target_socket.send(serialized.encode('utf-8'))
                return True
            return False
                
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def create_room(self) -> Optional[str]:
        """Create a new game room (server)"""
        return self.start_server(self.port)
    
    def join_room(self, room_code: str) -> bool:
        """Join an existing game room (client)"""
        try:
            # Parse room code (format: IP:PORT)
            parts = room_code.split(':')
            if len(parts) != 2:
                print("Invalid room code format. Use: IP:PORT")
                return False
            
            host = parts[0]
            port = int(parts[1])
            
            return self.connect_to_server(host, port)
        except ValueError:
            print("Invalid room code format")
            return False
    
    def send_player_choice(self, choice: str):
        """Send the player's choice to the opponent"""
        return self.send_message(NetworkMessageType.PLAYER_CHOICE, {"choice": choice})
    
    def disconnect(self):
        """Disconnect from the current game"""
        if self.connected:
            self.connected = False
            try:
                if self.socket:
                    self.socket.close()
                if self.client_socket:
                    self.client_socket.close()
            except:
                pass
            print("Disconnected")

# Example usage:
if __name__ == "__main__":
    import time
    
    def handle_choice(message):
        print(f"Opponent choice: {message}")
    
    # Server
    server = NetworkManager()
    room_code = server.create_room()
    print(f"Room created with code: {room_code}")
    server.set_message_handler(NetworkMessageType.PLAYER_CHOICE, handle_choice)
    
    # Give server time to start
    time.sleep(1)
    
    # Client
    client = NetworkManager()
    if room_code and client.join_room(room_code):
        print("Connected to room!")
        time.sleep(1)
        client.send_player_choice("rock")
    
    # Keep the program running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.disconnect()
        client.disconnect()


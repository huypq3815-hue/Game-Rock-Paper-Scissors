import socket
import threading
import json
import time
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

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
        self.message_handlers: Dict[NetworkMessageType, Callable[[Dict[str, Any]], None]] = {}
        self.receive_thread: Optional[threading.Thread] = None
        self.buffer_size = 4096
        self.is_server = False
        self.local_ip = self._get_local_ip()
        
        # Server-specific
        self.client_sockets: List[socket.socket] = []
        self.client_threads: List[threading.Thread] = []

    # -----------------------
    # Helper methods
    # -----------------------
    def _log(self, msg: str):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def set_message_handler(self, message_type: NetworkMessageType, handler: Callable[[Dict[str, Any]], None]):
        self.message_handlers[message_type] = handler

    # -----------------------
    # Server methods
    # -----------------------
    def start_server(self, port: int = 5555) -> Optional[str]:
        """Start server and accept multiple clients"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, port))
            self.socket.listen(5)
            self.connected = True
            self.is_server = True
            self.port = port
            self.room_code = f"{self.local_ip}:{port}"

            self.receive_thread = threading.Thread(target=self._accept_clients, daemon=True)
            self.receive_thread.start()

            self._log(f"Server started on {self.room_code}")
            return self.room_code
        except Exception as e:
            self._log(f"Failed to start server: {e}")
            return None

    def _accept_clients(self):
        while self.connected:
            try:
                client_socket, address = self.socket.accept()
                self._log(f"Client connected: {address}")
                self.client_sockets.append(client_socket)
                t = threading.Thread(target=self._handle_client, args=(client_socket,), daemon=True)
                t.start()
                self.client_threads.append(t)
            except Exception as e:
                if self.connected:
                    self._log(f"Error accepting client: {e}")

    def _handle_client(self, client_socket: socket.socket):
        buffer = ""
        try:
            while self.connected:
                data = client_socket.recv(self.buffer_size)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    if message.strip():
                        self._process_message(message, client_socket)
        except Exception as e:
            self._log(f"Error handling client: {e}")
        finally:
            self.client_sockets.remove(client_socket)
            client_socket.close()
            self._log(f"Client disconnected")

    # -----------------------
    # Client methods
    # -----------------------
    def connect_to_server(self, host: str, port: int) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            self.is_server = False
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            self._log(f"Connected to server {host}:{port}")
            return True
        except Exception as e:
            self._log(f"Failed to connect to server: {e}")
            return False

    def _receive_messages(self):
        buffer = ""
        while self.connected and self.socket:
            try:
                data = self.socket.recv(self.buffer_size)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    if message.strip():
                        self._process_message(message)
            except Exception as e:
                if self.connected:
                    self._log(f"Error receiving message: {e}")
                break

    # -----------------------
    # Common methods
    # -----------------------
    def _process_message(self, message: str, client_socket: Optional[socket.socket] = None):
        try:
            msg = json.loads(message)
            msg_type = NetworkMessageType(msg.get("type"))
            if msg_type in self.message_handlers:
                self.message_handlers[msg_type](msg)
        except Exception as e:
            self._log(f"Invalid message format: {e}")
            if self.is_server and client_socket:
                self.send_message(NetworkMessageType.ERROR, {"error": str(e)}, client_socket)

    def send_message(self, msg_type: NetworkMessageType, data: Optional[Dict[str, Any]] = None, target_socket: Optional[socket.socket] = None) -> bool:
        if not self.connected:
            return False
        try:
            message = json.dumps({"type": msg_type.value, "timestamp": time.time(), "data": data or {}}) + "\n"
            if self.is_server:
                sockets = [target_socket] if target_socket else self.client_sockets
                for s in sockets:
                    s.send(message.encode("utf-8"))
            else:
                if self.socket:
                    self.socket.send(message.encode("utf-8"))
            return True
        except Exception as e:
            self._log(f"Error sending message: {e}")
            return False

    # -----------------------
    # Convenience methods
    # -----------------------
    def create_room(self) -> Optional[str]:
        return self.start_server(self.port)

    def join_room(self, room_code: str) -> bool:
        try:
            host, port = room_code.split(":")
            return self.connect_to_server(host, int(port))
        except Exception:
            self._log("Invalid room code format")
            return False

    def send_player_choice(self, choice: str):
        self.send_message(NetworkMessageType.PLAYER_CHOICE, {"choice": choice})

    def disconnect(self):
        self.connected = False
        try:
            if self.socket:
                self.socket.close()
            for s in self.client_sockets:
                s.close()
        except:
            pass
        self._log("Disconnected")

#network.py
import socket
import json

class Network:
    def __init__(self, server_ip="127.0.0.1", port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = port
        self.addr = (self.server, self.port)
        self.player_id = None
        self.num = 0
        self.connected = False
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            init_raw = self.client.recv(2048).decode('utf-8')
            init_data = json.loads(init_raw)
            self.player_id = str(init_data["player_id"])
            self.num = init_data["num"]
            self.connected = True
            print(f"[NETWORK] Connected as Player ID: {self.player_id}")
        except Exception as e:
            print(f"[NETWORK ERROR] Failed to connect to server: {e}")
            self.connected = False

    def send(self, data):
        if not self.connected:
            return {}
        try:
            # Send serialized JSON data terminated with newline
            self.client.sendall((json.dumps(data) + "\n").encode('utf-8'))
            
            # Receive response from server
            response_raw = self.client.recv(2048).decode('utf-8')
            if not response_raw:
                return {}
            
            lines = response_raw.strip().split("\n")
            return json.loads(lines[-1])
        except Exception as e:
            print(f"[NETWORK ERROR] Transmission failed: {e}")
            self.connected = False
            return {}
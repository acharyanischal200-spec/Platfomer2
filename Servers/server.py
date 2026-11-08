# server.py
import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}...")
except Exception as e:
    print(f"[ERROR] Could not start server: {e}")
    exit()

players = {}
connected_clients = {}
player_counter = 0

def client_handler(conn, addr, player_id):
    global players
    print(f"[NEW CONNECTION] Player {player_id} connected from {addr}")
    
    # Send initial assignment (player_id and assigned character index)
    init_data = {"player_id": str(player_id), "num": player_id % 4}
    try:
        conn.sendall(json.dumps(init_data).encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Failed sending initial data to Player {player_id}: {e}")
        conn.close()
        return

    buffer = ""
    while True:
        try:
            data = conn.recv(2048)
            if not data:
                break

            buffer += data.decode('utf-8')
            
            # Process complete JSON lines or chunks
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    p_data = json.loads(line)
                    players[str(player_id)] = p_data

            # Broadcast all player positions back to client
            conn.sendall((json.dumps(players) + "\n").encode('utf-8'))

        except Exception:
            break

    print(f"[DISCONNECT] Player {player_id} disconnected.")
    if str(player_id) in players:
        del players[str(player_id)]
    conn.close()

def main():
    global player_counter
    while True:
        conn, addr = server.accept()
        p_id = player_counter
        player_counter += 1
        thread = threading.Thread(target=client_handler, args=(conn, addr, p_id))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()

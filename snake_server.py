import numpy as np
import socket
import threading
from _thread import start_new_thread
import pickle
from snake import SnakeGame
import uuid
import time
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
import base64

# Generate RSA keys
random_generator = Random.new().read
rsa = RSA.generate(2048, random_generator)
private_key = PKCS1_cipher.new(rsa)
public_key = PKCS1_cipher.new(rsa.publickey())

def encrypt_with_key(data, key):
    encoded = key.encrypt(data.encode())
    return base64.b64encode(encoded)

def decrypt(data):
    decoded = private_key.decrypt(base64.b64decode(data), None)
    return decoded.decode()

# Global variables
lock = threading.RLock()
clients = []
client_keys = {}

# Server configuration
server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((server, port))
s.listen(10)

print("Waiting for a connection, Server Started")

game = SnakeGame(20)
game_state = ""
interval = 0.2
moves_queue = set()

def broadcast(message):
    for client in clients:
        msg = encrypt_with_key(message, client_keys[client])
        client.send(msg)

def game_thread():
    global game, moves_queue, game_state
    while True:
        with lock:
            game.move(moves_queue)
            moves_queue = set()
            game_state = game.get_state()
        time.sleep(interval)

def accept_thread(conn, addr):
    global game
    unique_id = str(uuid.uuid4())
    rgb_colors_list = ["red", "green", "blue", "yellow", "orange"]
    color = rgb_colors_list[np.random.randint(0, len(rgb_colors_list))]

    # Receive client's public key
    public_key_data_client = conn.recv(1024).decode()
    public_key_client = PKCS1_cipher.new(RSA.importKey(public_key_data_client))
    conn.send(public_key.publickey().exportKey())

    with lock:
        game.add_player(unique_id, color=color)
        clients.append(conn)
        client_keys[conn] = public_key_client

    try:
        while True:
            raw_data = decrypt(conn.recv(500))
            if not raw_data:
                continue

            data_type, data = raw_data.split("***")

            with lock:
                conn.send(encrypt_with_key("***game***" + game_state, public_key_client))

                if data_type == "talk":
                    broadcast("***talk***User " + unique_id + " says: " + data)
                elif data in ["up", "down", "left", "right"]:
                    moves_queue.add((unique_id, data))
                elif data == "reset":
                    game.reset_player(unique_id)
                elif data == "quit":
                    game.remove_player(unique_id)
                    clients.remove(conn)
                    break

        conn.close()
    except Exception as e:
        with lock:
            game.remove_player(unique_id)
            clients.remove(conn)
        print(e)

def main():
    start_new_thread(game_thread, ())

    while True:
        conn, addr = s.accept()
        start_new_thread(accept_thread, (conn, addr))

if __name__ == "__main__":
    main()

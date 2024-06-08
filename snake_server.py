import numpy as np
import socket
from _thread import *
import pickle
from snake import SnakeGame
import uuid
import time 
import threading
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
import base64
 
# get random offset.
random_generator = Random.new().read 

# generate private key.
rsa = RSA.generate(2048, random_generator)  

# export private key
private_key_data = rsa.exportKey()   
private_key = PKCS1_cipher.new(RSA.importKey(private_key_data))
 
# export public key
public_key_data = rsa.publickey().exportKey()   
public_key = PKCS1_cipher.new(RSA.importKey(public_key_data))


def encryptWithKey(data, key):
    encoded = key.encrypt(data.encode())
    return base64.b64encode(encoded)


def decrypt(data):
    decoded = private_key.decrypt(base64.b64decode(data), 0)
    return decoded.decode()


lock = threading.RLock()
clients = []
client_keys = {}

# server = "10.11.250.207"
server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

counter = 0 
rows = 20 

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(10)
# s.settimeout(0.5)
print("Waiting for a connection, Server Started")

game = SnakeGame(rows)
game_state = "" 
last_move_timestamp = time.time()
interval = 0.2
moves_queue = set()


def broadcast(message):
    print("broadcast", len(clients), message)
    for client in clients:
        msg = encryptWithKey(message, client_keys[client])
        client.send(msg)


def game_thread(): 
    global game, moves_queue, game_state 
    while True:
        lock.acquire()
        last_move_timestamp = time.time()
        game.move(moves_queue)
        moves_queue = set()
        game_state = game.get_state()
        print(game_state)
        lock.release()
        while time.time() - last_move_timestamp < interval: 
            time.sleep(0.1) 


rgb_colors = {
    "red": (255, 0, 0),
    "green": (150, 200, 150),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
} 
 
rgb_colors_list = list(rgb_colors.values())


def accept_thread(conn, addr): 
    global counter, game
 
    unique_id = str(uuid.uuid4())
    color = rgb_colors_list[np.random.randint(0, len(rgb_colors_list))]
    
    # read public key of client.
    public_key_data_client = conn.recv(1024).decode()
    public_key_client = PKCS1_cipher.new(RSA.importKey(public_key_data_client))
    
    # send server's public key
    conn.send(public_key_data)
                
    lock.acquire()
    game.add_player(unique_id, color=color) 
    clients.append(conn)
    client_keys[conn] = public_key_client
    lock.release()
    
    try:
        user_quit = False
        while not user_quit: 
            raw_data = decrypt(conn.recv(500))
            print("received", raw_data)
            
            if not raw_data:
                continue
            
            data_type, data = raw_data.split("***")
            
            lock.acquire()
            conn.send(encryptWithKey("***game***" + game_state, public_key_client))
        
            if data_type == "talk":
                broadcast("***talk***User " + unique_id + " says: " + data)
            else:
                if not data:
                    print("no data received from client")
                    user_quit = True 
                elif data == "get": 
                    # print("received get")
                    pass 
                elif data == "quit":
                    print("received quit")
                    game.remove_player(unique_id)
                    clients.remove(conn)
                    user_quit = True
                elif data == "reset": 
                    print("received reset")
                    game.reset_player(unique_id)
        
                elif data in ["up", "down", "left", "right"]: 
                    move = data
                    print("received", move)
                    moves_queue.add((unique_id, move))
                    
                else:
                    print("Invalid data received from client:", data)
            lock.release()
        conn.close()
    except Exception as e:
        game.remove_player(unique_id)
        clients.remove(conn)
        print(e)
    
            
def main(): 
    global counter, game

    start_new_thread(game_thread, ())
    
    while True:
        conn, addr = s.accept()
        print("Connected to:", addr)
        start_new_thread(accept_thread, (conn, addr))

 
if __name__ == "__main__": 
    main()

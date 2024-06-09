import numpy as np
import pygame
import socket
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
import base64
import threading

# Initialize Pygame
pygame.init()

# Screen dimensions and grid settings
width = 500
rows = 20

# Generate RSA keys for secure communication
random_generator = Random.new().read
rsa = RSA.generate(2048, random_generator)
private_key_data = rsa.exportKey()
private_key = PKCS1_cipher.new(RSA.importKey(private_key_data))
public_key_data = rsa.publickey().exportKey()
public_key = PKCS1_cipher.new(RSA.importKey(public_key_data))

# Functions for encryption and decryption
def encrypt_with_key(data, key):
    encoded = key.encrypt(data.encode())
    return base64.b64encode(encoded)

def decrypt(data):
    decoded = private_key.decrypt(base64.b64decode(data), None)
    return decoded.decode()

# Socket setup
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "localhost"
port = 5555
addr = (server, port)
s.connect(addr)

# Exchange public keys
s.send(public_key_data)
public_key_data_server = s.recv(1024).decode()
public_key_server = PKCS1_cipher.new(RSA.importKey(public_key_data_server))

game_state = ""
flag = True

# Function to send data to the server
def send(data, receive=False):
    if not data.startswith("talk***"):
        data = "game***" + data
    try:
        s.send(encrypt_with_key(data, public_key_server))
        if receive:
            state = decrypt(s.recv(2048))
            tokens = [x for x in state.split("***") if len(x) > 0]
            for i in range(0, len(tokens), 2):
                data_type = tokens[i]
                pos = tokens[i + 1]
                if data_type == "talk":
                    print(pos)
            return state
    except socket.timeout as e:
        print(str(e))
    return None

def receive():
    try:
        state = decrypt(s.recv(2048))
        tokens = [x for x in state.split("***") if len(x) > 0]
        for i in range(0, len(tokens), 2):
            data_type = tokens[i]
            pos = tokens[i + 1]
            if data_type == "talk":
                print(pos)
        return state
    except socket.timeout as e:
        print(str(e))
    return None

# Drawing functions
def draw_grid(w, rows, surface):
    size_btwn = w // rows
    for l in range(rows):
        x = y = size_btwn * (l + 1)
        pygame.draw.line(surface, (128, 0, 128), (x, 0), (x, w))
        pygame.draw.line(surface, (128, 0, 128), (0, y), (w, y))

def draw_objects(surface, positions, color=None, eye=False):
    dis = width // rows
    if color is None:
        color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
    for i, j in positions:
        pygame.draw.rect(surface, color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eye:
            centre = dis // 2
            radius = 3
            circle_mid = (i * dis + centre - radius, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circle_mid, radius)
            pygame.draw.circle(surface, (0, 0, 0), circle_mid, radius)

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def draw(surface, players, snacks):
    surface.fill((0, 0, 0))
    draw_grid(width, rows, surface)
    for player in players:
        color = tuple(map(int, player[0][1:-1].split(',')))
        draw_objects(surface, player[1:], color=color, eye=True)
    draw_objects(surface, snacks, (0, 255, 0))
    pygame.display.update()

# Thread to handle receiving game state from the server
def handle_client():
    global game_state
    while flag:
        game_state = receive()

def main():
    global flag

    thread_reading = threading.Thread(target=handle_client)
    thread_reading.start()

    talk_text = ""
    win = pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()

    try:
        while flag:
            events = pygame.event.get()
            pygame.time.delay(100)
            clock.tick(10)
            state = None
            if events:
                for event in events:
                    if event.type == pygame.QUIT:
                        flag = False
                        send("quit")
                        pygame.quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            send("up")
                        elif event.key == pygame.K_DOWN:
                            send("down")
                        elif event.key == pygame.K_LEFT:
                            send("left")
                        elif event.key == pygame.K_RIGHT:
                            send("right")
                        elif event.key == pygame.K_SPACE:
                            send("reset")
                            talk_text += " "
                        elif event.key == pygame.K_RETURN:
                            if talk_text:
                                send(f"talk***{talk_text}")
                                talk_text = ""
                        else:
                            raw_ch = event.key
                            if 0 <= raw_ch <= 0x10FFFF:
                                ch = chr(raw_ch)
                                talk_text += ch.strip()
                            if raw_ch == 1073741912:
                                if talk_text:
                                    send(f"talk***{talk_text}")
                                    talk_text = ""
            else:
                send("get")

            state = game_state
            if state is None:
                continue

            tokens = [x for x in state.split("***") if len(x) > 0]
            snacks, players = [], []

            raw_players, raw_snacks = [part.split("**") for part in tokens[1].split("|")]

            for raw_player in raw_players:
                raw_positions = raw_player.split("*")
                positions = [raw_positions[0]] + [(int(p.split(',')[0]), int(p.split(',')[1])) for p in raw_positions[1:] if p]
                players.append(positions)

            for raw_snack in raw_snacks:
                nums = raw_snack.split(')')[0].split('(')[1].split(',')
                snacks.append((int(nums[0]), int(nums[1])))

            draw(win, players, snacks)
            draw_text(win, " ", 36, width // 2, width // 2, (255, 255, 255))
            pygame.display.update()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        send("right")

if __name__ == "__main__":
    main()

import numpy as np
import pygame
import socket
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
import base64
import threading

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


# decrypt with self's private key.
def decrypt(data):
    decoded = private_key.decrypt(base64.b64decode(data), 0)
    return decoded.decode()


# Define screen dimensions and clock
pygame.init()
global width, rows
width = 500
rows = 20
################################################################ 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "localhost"
port = 5555
# socket
addr = (server, port)
s.connect(addr)
s.send(public_key_data)  # send public key to server.
public_key_data_server = s.recv(1024).decode()  # read public key of server.
public_key_server = PKCS1_cipher.new(RSA.importKey(public_key_data_server))
game_state = ""
flag = True
    
# send data to the server
def send(data, receive=False):
    if not data.startswith("talk***"):
        data = "game***" + data

    try: 
        s.send(encryptWithKey(data, public_key_server))
        
        if receive == True:
            state = decrypt(s.recv(2048))
            tokens = [x for x in state.split("***") if len(x) > 0]

            for i in range(0, len(tokens), 2):
                data_type = tokens[i]
                pos = tokens[i + 1]
                if data_type == "talk":
                    print(pos)
                    continue
            return state
        else:
            return None
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
                continue
        return state
    except socket.timeout as e:
        print(str(e))
        return None
    
###############################################################


# draw the grids
def drawGrid(w, rows, surface):
    sizeBtwn = w // rows
    x = 0
    y = 0
    for l in range (rows):
        x = x + sizeBtwn
        y = y + sizeBtwn
        pygame.draw.line(surface, (128, 0, 128), (x, 0), (x, w))
        pygame.draw.line(surface, (128, 0, 128), (0, y), (w, y))


# draw snacks, snake  
def drawObjects(surface, position, color=None, eye=False):
    global w
    
    w = 500
    rows = 20
    dis = w // rows
    if color is None:
            color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
    for posId, poss in enumerate(position):
        i, j = poss
        
        pygame.draw.rect(surface, color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eye and posId == 0:
            centre = dis // 2
            radius = 3
            circleMid = (i * dis + centre - radius, j * dis + 8)
            circleMid2 = (i * dis + centre - radius, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMid, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMid2, radius)

            
def draw_text(surface, text, size, x, y, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

            
def draw(surface, players, snacks):
    surface.fill((0, 0, 0))
    drawGrid(width, rows, surface)
    for _, player in enumerate(players):
        color = player[0].strip()
        color = color[1: len(color) - 1]
        color = color.split(',')
        color = (int(color[0].strip()), int(color[1].strip()), int(color[2].strip()))
        player = player[1:]
        drawObjects(surface, player, color=color, eye=True)
    drawObjects(surface, snacks, (0, 255, 0))
    pygame.display.update()
 

def handle_client():
    global game_state
    while flag:
        game_state = receive()
        
        #print(game_state)
    
    
def main():
    global flag
    
    
    thread_reading = threading.Thread(target=handle_client, args=( )) 
    thread_reading.start()
    
    talk_text = ""
    
    print("START MAIN\n")
    win = pygame.display.set_mode((500, 500))
 

    clock = pygame.time.Clock()
    # print("AFTER SETTING UP FLAG\n")
    
    try:
        while flag == True:
            # print("into WHILE LOOP\n")
            events = pygame.event.get()
            pygame.time.delay(100)
            clock.tick(10)
            
            state = None
            if len(events) > 0:
                for event in events:
                # for event in pygame.event.get(): 
                    if event.type == pygame.QUIT: 
                        flag = False
                        state = send("quit", receive=False)
                        pygame.quit()
                    # send server the action
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            state = send("up", receive=False)
                          
                        elif event.key == pygame.K_DOWN:
                            state = send("down", receive=False)
                           
                        elif event.key == pygame.K_LEFT:
                            state = send("left", receive=False)
                        
                        elif event.key == pygame.K_RIGHT:
                            state = send("right", receive=False)
            
                        elif event.key == pygame.K_SPACE:
                            state = send("reset", receive=False)
                            print(" ", end='', flush=True)
                            talk_text += " "
                        elif event.key == pygame.K_RETURN:
                            # print("return", flush=True)
                            if len(talk_text) > 0:
                                state = send("talk***" + talk_text, receive=False)
                                talk_text = ""
                                print("", flush=True)
                        else:
                            raw_ch = event.key
                            # print("\nraw_ch:", raw_ch, flush=True)
                            if 0 <= raw_ch <= 0x10ffff:
                                ch = chr(raw_ch)
                                talk_text += ch
                                talk_text = talk_text.strip()
                                print(ch.strip(), end='', flush=True)
                            if raw_ch == 1073741912:
                                if len(talk_text) > 0:
                                    state = send("talk***" + talk_text, receive=False)
                                    talk_text = ""
                                    print("", flush=True)
                        # no press movement, send get
            else: 
                state = send("get", receive=False)  
 
            state = game_state
            if state == None:
                continue
            
            tokens = [x for x in state.split("***") if len(x) > 0]
            
            for i in range(0, len(tokens), 2):
                data_type = tokens[i]
                pos = tokens[i + 1]
                # print(data_type, pos)
     
                if data_type == "talk":
                    continue
         
                snacks, players = [], []
                
                # print("pos:", pos)
                raw_players, raw_snacks = [part.split("**") for part in pos.split("|")]
                
                if raw_players == '':
                    pass
                else: 
                    for raw_player in raw_players:
                        raw_positions = raw_player.split("*")
                        if len(raw_positions) == 0:
                            continue
                        # print("No PROBLEM HERE\n")
                        positions = [raw_positions[0]]
                        raw_positions = raw_positions[1:]
                        for raw_position in raw_positions:
                            if raw_position == "":
                                continue
                            nums = raw_position.split(')')[0].split('(')[1].split(',')
                            positions.append((int(nums[0]), int(nums[1])))
                        players.append(positions)
                # print("No PROBLEM HERE EITHER\n")
                for i in range(len(raw_snacks)):
                    nums = raw_snacks[i].split(')')[0].split('(')[1].split(',')
                    snacks.append((int(nums[0]), int(nums[1])))
     
                draw(win, players, snacks)
                draw_text(win, " ", 36, width // 2, width // 2, (255, 255, 255))
                pygame.display.update()  
    except Exception as e:
        print(e)
    except KeyboardInterrupt as e:
        send("right", receive=False)
        print(e)
        
    # Clean up and close the socket
    
    
if __name__ == "__main__":
    main()

# receive game state from the server

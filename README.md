# Multiplayer Snake Game

This repository contains a multiplayer Snake game implemented in Python, using sockets for communication between the server and multiple clients. The game includes encrypted communication using RSA.

## Project Structure

- **snake.py**: Contains the main game logic.
- **snake_server.py**: The server-side script.
- **snake_client.py**: The client-side script.

## Setup Instructions

### Prerequisites

- Python 3.x
- Pygame (`pip install pygame`)
- PyCryptoDome (`pip install pycryptodome`)

### Running the Server

1. **Navigate to the project directory**:
    ```sh
    cd path/to/project
    ```

2. **Run the server script**:
    ```sh
    python snake_server.py
    ```

### Running the Client

1. **Navigate to the project directory**:
    ```sh
    cd path/to/project
    ```

2. **Run the client script**:
    ```sh
    python snake_client.py
    ```

### Game Controls

- **Arrow Keys**: Control the direction of the snake.
- **Space**: Reset the game.
- **Enter**: Send a message to all players.

## File Descriptions

### snake.py

This file contains the main logic for the Snake game. It includes classes and methods to handle game state, player movement, and game updates.

### snake_server.py

This file sets up a server that handles multiple clients. The server:
- Accepts new client connections.
- Manages the game state and player movements.
- Uses RSA for encrypted communication with clients.

### snake_client.py

This file connects to the server and allows a user to play the game. The client:
- Sends player movements to the server.
- Receives game state updates from the server.
- Displays the game using Pygame.

## Encryption

The communication between the server and clients is encrypted using RSA. Each client sends its public key to the server, and the server uses this key to encrypt messages sent to the client.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License.

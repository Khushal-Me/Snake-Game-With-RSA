import random
import pygame

# Cube class represents a single cube in the game grid
class Cube:
    rows = 20
    w = 500

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 0, 0)):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny  # "L", "R", "U", "D"
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i, j = self.pos
        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circle_middle = (i * dis + centre - radius, j * dis + 8)
            circle_middle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circle_middle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circle_middle2, radius)


# Snake class represents the snake in the game
class Snake:
    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos)
        self.body = [self.head]
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def move(self, key):
        if isinstance(key, str):
            self._change_direction(key)
        self._update_body_positions()

    def _change_direction(self, key):
        # Change the direction of the snake based on the key input
        if key == 'left':
            self.dirnx, self.dirny = -1, 0
        elif key == 'right':
            self.dirnx, self.dirny = 1, 0
        elif key == 'up':
            self.dirnx, self.dirny = 0, -1
        elif key == 'down':
            self.dirnx, self.dirny = 0, 1
        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

    def _update_body_positions(self):
        # Update the positions of the snake's body segments
        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        # Reset the snake to its initial state
        self.head = Cube(pos)
        self.body = [self.head]
        self.turns = {}
        self.dirnx, self.dirny = 0, 1

    def add_cube(self):
        # Add a new cube to the snake's body
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            new_pos = (tail.pos[0] - 1, tail.pos[1])
        elif dx == -1 and dy == 0:
            new_pos = (tail.pos[0] + 1, tail.pos[1])
        elif dx == 0 and dy == 1:
            new_pos = (tail.pos[0], tail.pos[1] - 1)
        else:
            new_pos = (tail.pos[0], tail.pos[1] + 1)

        new_cube = Cube(new_pos, color=self.color)
        new_cube.dirnx, new_cube.dirny = dx, dy
        self.body.append(new_cube)

    def draw(self, surface):
        # Draw the snake on the game surface
        for i, c in enumerate(self.body):
            c.draw(surface, eyes=(i == 0))

    def get_positions(self):
        # Get the positions of the snake's body segments
        positions = [p.pos for p in self.body]
        positions.insert(0, self.color)
        return "*".join(map(str, positions))


# SnakeGame class represents the game itself
class SnakeGame:
    def __init__(self, rows):
        self.rows = rows
        self.players = {}
        self.snacks = [Cube(random_snack(rows)) for _ in range(5)]

    def add_player(self, user_id, color):
        # Add a new player to the game
        self.players[user_id] = Snake(color, (10, 10))

    def remove_player(self, user_id):
        # Remove a player from the game
        self.players.pop(user_id)

    def move(self, moves):
        # Move the players in the game based on the given moves
        move_ids = {m[0] for m in moves}
        still_ids = set(self.players) - move_ids

        for move in moves:
            self.move_player(move[0], move[1])

        for still_id in still_ids:
            self.move_player(still_id, None)

        for p_id in self.players:
            if self.check_collision(p_id):
                self.reset_player(p_id)

    def move_player(self, user_id, key=None):
        # Move a player in the game
        if user_id in self.players:
            self.players[user_id].move(key)

    def reset_player(self, user_id):
        # Reset a player to its initial state
        x_start = random.randrange(1, self.rows - 1)
        y_start = random.randrange(1, self.rows - 1)
        self.players[user_id].reset((x_start, y_start))

    def check_collision(self, user_id):
        # Check if a player has collided with a snack or itself
        player = self.players[user_id]
        for snack in self.snacks:
            if player.head.pos == snack.pos:
                self.snacks.remove(snack)
                self.snacks.append(Cube(random_snack(self.rows)))
                player.add_cube()

        if player.head.pos in [c.pos for c in player.body[1:]]:
            return True

        x, y = player.head.pos
        if x < 0 or y < 0 or x >= self.rows or y >= self.rows:
            return True

        return False

    def get_state(self):
        # Get the current state of the game
        players_pos = [p.get_positions() for p in self.players.values()]
        players_pos_str = "**".join(players_pos)
        snacks_pos = "**".join(map(str, [s.pos for s in self.snacks]))
        return players_pos_str + "|" + snacks_pos


def random_snack(rows):
    # Generate random coordinates for a snack
    return random.randrange(1, rows - 1), random.randrange(1, rows - 1)


if __name__ == "__main__":
    pass

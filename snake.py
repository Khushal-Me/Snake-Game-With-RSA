import random
import pygame
import random




class cube():
    rows = 20
    w = 500
    def __init__(self, start, dirnx=1, dirny=0, color=(255,0,0)):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny # "L", "R", "U", "D"
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos  = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)
            

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]
        
        pygame.draw.rect(surface, self.color, (i*dis+1,j*dis+1,dis-2,dis-2))
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis+centre-radius,j*dis+8)
            circleMiddle2 = (i*dis + dis -radius*2, j*dis+8)
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)
        


class snake():
    body = []
    turns = {}
    
    def __init__(self, color, pos):
        #pos is given as coordinates on the grid ex (1,5)
        self.color = color
        self.head = cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
    
    def move(self, key) : 
        
        if isinstance(key, str) :
            if key == 'left' : 
                self.dirnx = -1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
            elif key == 'right' : 
                self.dirnx = 1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
            elif key == 'up' : 
                self.dirnx = 0
                self.dirny = -1
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
            elif key == 'down' :
                self.dirnx = 0
                self.dirny = 1
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        else : 
            # continue in same direction
            pass

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body)-1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx,c.dirny)
        
    def reset(self,pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0]-1,tail.pos[1]), color=self.color))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0]+1,tail.pos[1]), color=self.color))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0],tail.pos[1]-1), color=self.color))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0],tail.pos[1]+1), color=self.color))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy
    
    def draw(self, surface):
        for i,c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)
    
    def get_pos(self) : 
        positions = [p.pos for p in self.body]
        positions.insert(0, self.color)
        pos_str = "*".join([str(p) for p in positions])
        return pos_str


class SnakeGame:

    def __init__(self, rows):
        self.rows = rows
        self.players = {}
        self.snacks = [cube(randomSnack(rows)) for _ in range(5)]

    def add_player(self, user_id, color):
        self.players[user_id] = snake(color, (10, 10))

    def remove_player(self, user_id):
        self.players.pop(user_id)

    def move(self, moves):
        moves_ids = set([m[0] for m in moves])
        still_ids = set(self.players.keys()) - moves_ids
        for move in moves:
            self.move_player(move[0], move[1])

        for still_id in still_ids:
            self.move_player(still_id, None)

        for p_id in self.players.keys():
            if self.check_collision(p_id):
                self.reset_player(p_id)

    def move_player(self, user_id, key=None):
        if user_id in self.players:
            self.players[user_id].move(key)

    def reset_player(self, user_id):
        x_start = random.randrange(1, self.rows - 1)
        y_start = random.randrange(1, self.rows - 1)
        self.players[user_id].reset((x_start, y_start))

    def get_player(self, user_id):
        return self.players[user_id].head.pos

    def check_collision(self, user_id):
        for snack in self.snacks:
            if self.players[user_id].head.pos == snack.pos:
                self.snacks.remove(snack)
                self.snacks.append(cube(randomSnack(self.rows)))
                self.players[user_id].addCube()

        if self.players[user_id].head.pos in list(map(lambda z: z.pos, self.players[user_id].body[1:])):
            return True

        if (
            self.players[user_id].head.pos[0] < 0
            or self.players[user_id].head.pos[1] < 0
            or self.players[user_id].head.pos[0] > self.rows - 1
            or self.players[user_id].head.pos[1] > self.rows - 1
        ):
            return True

        return False

    def get_state(self):
        players_pos = [p.get_pos() for p in self.players.values()]
        players_pos_str = "**".join(players_pos)
        snacks_pos = "**".join([str(s.pos) for s in self.snacks])
        return players_pos_str + "|" + snacks_pos


    
def randomSnack(rows):
    x = random.randrange(1,rows-1)
    y = random.randrange(1,rows-1)
    return (x,y)

    
if __name__ == "__main__":
    pass
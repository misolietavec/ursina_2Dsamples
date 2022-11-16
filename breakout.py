from ursina import *
from random import randint, choice

HALF_WIDTH = 400
HALF_HEIGHT = 225
b_colors = (color.red, color.blue, color.yellow, color.green, color.magenta)


app = Ursina(size = (2 * HALF_WIDTH, 2* HALF_HEIGHT))
window.borderless = False
camera.orthographic = True
camera.fov = 2 * HALF_HEIGHT
mouse.visible = False

global game

class Game(Entity):
    def __init__(self):
        super().__init__()
        self.ball = Entity(model='circle', scale=16, collider='box')
        self.paddle = Entity(model='quad', scale= (120, 20), collider='box', 
                             color= color.orange)
        self.message = Text(text='You LOST', scale=2, origin=(0,0), 
                            collider="box", color=color.red)
        self.makebricks()
        self.setup()
         
    def setup(self):
        self.ball.x, self.ball.y, self.ball.dx, self.ball.dy = 0, -180, 2.5, 4 + randint (-1, 2)
        self.paddle.x, self.paddle.y = 0, -215
        self.message.visible = False
        self.active = True
         
    def makebricks(self):
        self.bricks = []
        x_pos, x_step, y_step = -340, 2 * 340 / 9, 22
        for row in range(10):
            y_pos = 180
            for col in range(4):
                brick = Entity(model = 'quad', x = x_pos, y = y_pos, 
                               scale = (x_step - 10, y_step -4),  collider='box', color = choice(b_colors))
                self.bricks.append(brick)
                y_pos -= y_step
            x_pos += x_step
             
    def reset(self):
        self.setup()
        for brick in self.bricks:
            destroy(brick)
        self.makebricks()    
        
    def update(self):
        if not self.active: return
        self.ball.x += self.ball.dx
        self.ball.y += self.ball.dy
        self.paddle.x = clamp(2 * HALF_WIDTH * mouse.x, -HALF_WIDTH + 40, HALF_WIDTH - 40)
        if self.ball.x < -HALF_WIDTH or self.ball.x > HALF_WIDTH: # left, right bounce
            self.ball.dx = -self.ball.dx
        if self.ball.y > HALF_HEIGHT:                  # ceiling bounce
            self.ball.dy = -self.ball.dy
        
        hit_info = self.ball.intersects()
        if hit_info.hit:        
            if hit_info.entity in self.bricks:
                destroy(hit_info.entity)
                self.bricks.remove(hit_info.entity)
                self.ball.dy = -self.ball.dy
            if hit_info.entity == self.paddle:
                self.ball.dy = -self.ball.dy
        self.active = not ((self.ball.y < -HALF_HEIGHT + 8) or (len(self.bricks) == 0))
        if not self.active:
            res = "You WON" if self.bricks == [] else "You LOST"
            self.message.text = res
            self.message.visible = True

game = Game()

def input(key):
    global game
    if key == "q":
        quit()         
    if key == "n":
        game.reset()
                
app.run()

from ursina import *

from random import choice

lbg = color.dark_gray 
red, orange, green = color.red, color.orange, color.green
states = [(red, orange, lbg), (lbg, lbg, green), (red, orange, green), 
          (lbg, orange, lbg), (red, lbg, lbg)]

WIDTH = 640
HEIGHT = 480
app = Ursina(size=(WIDTH, HEIGHT), title="Misfunctional Semaphore")
camera.orthographic = True
camera.fov = HEIGHT
window.borderless = False

Sky()

class Semaphore(Entity):
    def __init__(self):
        super().__init__()
        self.time = 0
        # z=0.01 ensures that lights are nearer to camera than the semrect
        self.semrect = Entity(model='quad', x=0, y=0, z= 1, 
                              scale=(WIDTH / 5, HEIGHT / 1.3), color=color.light_gray)         
        r, o, g = choice(states)
        self.rl = Entity(model='circle', scale=60, x = 0, y = HEIGHT / 5, color=r)
        self.ol = Entity(model='circle', scale=60, x = 0, y = 0, color=o)
        self.gl = Entity(model='circle', scale=60, x = 0, y = -HEIGHT / 5, color=g)
        self.time_text = Text(text='0', scale=2, origin=(0, 0), x=0, y=-0.44, color=color.white)


    def update(self):
        self.time += 1
        self.time_text.text = f'{self.time // 60}'
        if self.time == 4 * 60:
            old_status = (self.rl.color, self.ol.color, self.gl.color)
            status = choice(states)
            while status == old_status:
                status = choice(states)
            self.rl.color, self.ol.color, self.gl.color = status
            self.time = 0

def input(key):
    if key == "q":
        quit()
        
game = Semaphore()
app.run()

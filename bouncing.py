from ursina import *

WIDTH = 800
HEIGHT = 450
DIAM = 20

app = Ursina(size=(WIDTH, HEIGHT))
window.color = color.light_gray
window.borderless = False
camera.orthographic = True
camera.fov = HEIGHT

ball = Entity(model='circle', scale=DIAM, collider='box', 
              dx=5, dy=7, color=color.blue)


def update():
    ball.x += ball.dx
    ball.y += ball.dy
    
    if ball.x <= -WIDTH / 2 + DIAM  or ball.x >= WIDTH / 2 - DIAM:
        ball.dx = -ball.dx
    if ball.y <= -HEIGHT / 2 + DIAM  or ball.y >= HEIGHT / 2 - DIAM:        
        ball.dy = -ball.dy

def input(key):
    if key == "q":
        quit()
        
app.run()

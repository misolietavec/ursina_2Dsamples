# The Bird of Peace :-)

from ursina import Ursina, Entity, Sprite, window, camera, Animation
import math

WIDTH = 800
HEIGHT = 800
Sprite.ppu = 1.28
RADIUS = 375

app = Ursina(size=(WIDTH, HEIGHT))
window.borderless=False
camera.orthographic = True
camera.fov = HEIGHT

global angle
angle = 0

bird = Animation('flappy', collider='box', scale=50, y=RADIUS, z= -1)
earth = Sprite(texture="Earth_from_Space")

def update():
    global angle
    phi = math.radians(angle)
    bird.x = RADIUS * math.cos(phi)
    bird.y = RADIUS * math.sin(phi)
    bird.rotation_z = 90 - angle
    angle -= 0.5
    
app.run()

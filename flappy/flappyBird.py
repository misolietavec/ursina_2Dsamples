from ursina import Ursina, Entity, color, window, camera
from ursina import time, destroy, Sky, Animation
from random import randint
from time import sleep
from threading import Thread
 

WIDTH = 800
HEIGHT = 450
app = Ursina(size=(WIDTH, HEIGHT))
window.borderless=False
camera.orthographic = True
camera.fov = HEIGHT

Sky()
bird = Animation('flappy', collider='box', scale=(45, 45), y=225)

pipes = []

def add_pipe(seconds):
    while True:
        y = randint(140, 280)
        new_bottom = Entity(model='quad', texture='pipe-red', 
                            position=(450, 225), 
                            scale=(68, 338), collider='cube')

        new_top = Entity(model='quad', texture='pipe-green', position=(450, y), 
                         scale=(68, 338), collider='cube', rotation_z=180)
        new_bottom.y = y - 450
        pipes.extend((new_top, new_bottom))
        sleep(seconds)


daemon = Thread(target=add_pipe, args=(5,), daemon=True, name='AddPipes')


def update():
    bird.y = bird.y - 45 * time.dt
    for p in pipes:
        p.x = p.x - 45 * time.dt
        if p.x < -WIDTH / 2:
            destroy(p)
            pipes.remove(p)
            continue
        touch = bird.intersects()
        if touch.hit or bird.y < -225:
            bird.color=color.brown
            bird.y = -110  # or quit()
            bird.z = 0.2


def input(key):
    if key == 'space':
        bird.y = bird.y + 40
    if key == 'q':
        quit()


daemon.start()
app.run()

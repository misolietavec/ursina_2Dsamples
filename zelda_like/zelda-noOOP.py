from ursina import Ursina, Sprite, Entity, color, load_texture, window, \
     mouse, camera, held_keys, raycast, Vec3, destroy, Text

from numpy import array

H_WIDTH = 400
H_HEIGHT = 300
I_SIZE = 50

app = Ursina(size=(2 * H_WIDTH, 2 * H_HEIGHT))

window.borderless = False
mouse.visible = False
camera.orthographic = True
camera.fov = 2 * H_HEIGHT
Sprite.ppu = 1

minimap = load_texture('map')

monstersXY = [(875, -125), (1625, -125), (1625, 375), (2525, 425), (625, 425)]
spriteDict = {color.green: "tree", color.black: "ground",
              color.red: "boulder", color.yellow: "rock"}
directions = {(0, 1): (1, 2), (-1, 0): (3, 4),
              (0, -1): (5, 6), (1, 0): (7, 8)}
sworddirs = [(0, 1), (-1, 0), (0, -1), (1, 0)]

global GM, xtrans, ytrans, toMove

GM = array([[0] * 20 for col in range(64)], dtype=object)

monsters = []
for row in range(20):
    for col in range(64):
        pcolor = minimap.get_pixel(col, row)
        GM[col, row] = Sprite(spriteDict[pcolor], visible=False)
for ind in range(len(monstersXY)):
    xm, ym = monstersXY[ind]
    Mons = Sprite("monster_1", x=xm, y=ym, z=-0.1,
                  collider="sphere", visible=False)
    Mons.state = 10
    Mons.frame = Mons.dx = Mons.dy = 0
    monsters.append(Mons)

xtrans = 0   # 0, 16, 32, 48
ytrans = 0   # 0, 10
toMove = True

Link = Sprite("link_1", y=-100, z=-0.2)
Link.frame = Link.dx = Link.dy = Link.dir = 0
sword = Sprite(texture="sword_0", z=-0.1, visible=False)
sword.frame = sword.dir = sword.dx = sword.dy = 0

# left_bottom: x = -390, y=210
navig = Entity(model="quad", color=color.rgb(100, 100, 100),
                    x=-262, y=250, scale=(256, 80))
navig.lbx, navig.lby = -390, 210

def toMinimap(mx, my):
    mx = (400 + 50 * xtrans + Link.x) / 12.5
    my = (300 + 50 * ytrans + Link.y) / 12.5
    return (navig.lbx + mx, navig.lby + my)

lx, ly = toMinimap(Link.x, Link.y)
miniLink = Entity(model='quad', color=color.green, x=lx, y=ly, z=-0.1, scale=4)

Sprite(texture="logo", x=300, y=250, z=-0.1)
helptext = "Move by arrows\nSpace to use sword"
Text(text=helptext, scale=2, x=-0.16, y=0.465, color=color.green)


def updateGM():
    global GM, toMove
    if toMove:
        for cell in GM.flat:
            cell.visible = False
        for row in range(10):
            y = -H_HEIGHT + 25 + row * 50
            for col in range(16):
                tcol, trow = col + xtrans, row + ytrans
                GM[tcol, trow].visible = True
                x = -H_WIDTH + 25 + col * 50
                GM[tcol, trow].position = (x, y)
        for ind in range(len(monsters)):
            xm, ym = monstersXY[ind]
            xmt, ymt = xm - 50 * xtrans, ym - 50 * ytrans
            if (-400 <= xmt <= 400) and (-300 <= ymt <= 200):
                monsters[ind].visible = True
                monsters[ind].position = (xmt, ymt)
            else:
                monsters[ind].visible = False
        toMove = False


def testMove(Act):
    ox, oy = Act.x, Act.y
    cell_x, cell_y = in_cell(ox, oy)
    testx = ox + 25 * Act.dx
    testy = oy + 25 * Act.dy
    ncx, ncy = in_cell(testx, testy)
    if str(GM[ncx, ncy + 1].texture) != "ground.png":
        Act.dx = Act.dy = 0
    else:
        Act.x = ox + 2 * Act.dx
        Act.y = oy + 2 * Act.dy


def animActor(Act, actname):
    if Act.dx * Act.dy == 0:
        num1, num2 = directions[(Act.dx, Act.dy)]
        num = num1 if Act.frame <= 9 else num2
        Act.dir = int(num2 // 2) - 1
        Act.frame += 1
        Act.frame = Act.frame % 20
        Act.texture = f"{actname}_{num}"


def updateLink():
    if Link.dx or Link.dy:
        animActor(Link, "link")
        testMove(Link)
        moveMap()
        miniLink.x, miniLink.y = toMinimap(Link.x, Link.y) 


def moveMap():
    global xtrans, ytrans, toMove
    toMove = (not (-400 < Link.x < 400) or not (-300 < Link.y < 200))
    if toMove:
        if Link.x < -400:
            xtrans = max(0, xtrans - 16)
            Link.x = 800 + Link.x
        elif Link.x > 400:
            xtrans = min(48, xtrans + 16)
            Link.x = -800 + Link.x
        if Link.y < -300:
            ytrans = max(0, ytrans - 10)
            Link.y = 500 + Link.y
        elif Link.y > 200:
            ytrans = min(10, ytrans + 10)
            Link.y = -500 + Link.y


def updateSword():
    if sword.frame > 0:
        sdx, sdy = sword.dx, sword.dy
        sdir = 1 if (sword.frame > 5) else -1
        sword.x += sdir * sdx * 2
        sword.y += sdir * sdy * 2
        sword.frame -= 1
    else:
        sword.visible = False


def markMonsters():
    for Mon in monsters:
        if Mon.visible and sword.visible:
            sdx, sdy = sword.dx, sword.dy
            hitinfo = raycast(Link.position, Vec3(sdx, -sdy, 0),
                              distance=60)
            if hitinfo.hit:
                if hitinfo.entity == Mon:
                    Mon.state = 9
                    break


def updateMonsters():
    markMonsters()
    for Mon in monsters:
        if Mon.state < 10:
            Mon.rotation_z += 10
            Mon.state -= 1
        if Mon.state == 0:
            ind = monsters.index(Mon)
            destroy(Mon)
            del monsters[ind]
            del monstersXY[ind]
        if (Mon.state == 10) and Mon.visible:
            if (Mon.x > Link.x + 50):
                Mon.dx = -1
            else:
                if (Mon.x < Link.x - 50):
                    Mon.dx = 1
            if (Mon.y > Link.y + 50):
                Mon.dy = -1
            else:
                if (Mon.y < Link.y - 50):
                    Mon.dy = 1
            if Mon.dx or Mon.dy:
                animActor(Mon, "monster")
                testMove(Mon)


def update():
    updateGM()
    updateLink()
    updateSword()
    updateMonsters()


def in_cell(x, y):
    cell_x = int((x + 400) // 50) + xtrans
    cell_y = int((y + 250) // 50) + ytrans
    return (cell_x, cell_y)


def input(key):
    Link.dx = held_keys['right arrow'] - held_keys['left arrow']
    Link.dy = held_keys['up arrow'] - held_keys['down arrow']
    if key == "space":
        sword.dx, sword.dy = sworddirs[Link.dir]
        sword.frame = 10
        sword.texture = f"sword_{Link.dir}"
        sword.x = Link.x + 30 * sword.dx
        sword.y = Link.y - 35 * sword.dy
        sword.visible = True
    if key == "q":
        quit()


app.run()

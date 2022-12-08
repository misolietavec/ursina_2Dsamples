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

    
class ZeldaGame(Entity):
    def __init__(self):
        super().__init__()
        self.GM = array([[0] * 20 for col in range(64)], dtype=object)
        self.monsters = []
        for row in range(20):
            for col in range(64):
                pcolor = minimap.get_pixel(col, row)
                self.GM[col, row] = Sprite(spriteDict[pcolor], visible=False)
        for ind in range(len(monstersXY)):
            xm, ym = monstersXY[ind]
            Mons = Sprite("monster_1", x=xm, y=ym, z=-0.1,
                          collider="sphere", visible=False)
            Mons.state = 10
            self.monsters.append(Mons)
        self.xtrans = 0   # 0, 16, 32, 48
        self.ytrans = 0   # 0, 10
        self.monstate = 0
        self.toMove = True

        self.Link = Sprite("link_1", y=-100, z=-0.2)
        self.Link.frame = self.Link.dx = self.Link.dy = self.Link.dir = 0
        self.sword = Sprite(texture="sword_0", z=-0.1, visible=False)
        self.sword.frame = self.sword.dir = self.sword.dx = self.sword.dy = 0

        # left_bottom: x = -390, y=210  
        self.navigation = Entity(model="quad", color=color.rgb(100, 100, 100),
                                 x=-262, y=250, scale=(256, 80))
        mx = (400 + self.Link.x) / 12.5
        my = (300 + self.Link.y) / 12.5
        lb_x, lb_y = -390, 210 
        self.miniLink = Entity(model='quad', color=color.green, 
                               x=lb_x + mx, y= lb_y + my, z=-0.1, scale=4)
        self.navigation.lbx, self.navigation.lby = lb_x, lb_y
        
        Sprite(texture="logo", x=300, y=250, z=-0.1)
        helptext = "Move by arrows\nSpace to use sword"
        Text(text=helptext, scale=2, x=-0.16, y=0.465, color=color.green)
        
    def updateGM(self):
        if self.toMove:
            for cell in self.GM.flat:
                cell.visible = False
            for row in range(10):
                y = -H_HEIGHT + 25 + row * 50
                for col in range(16):
                    tcol, trow = col + self.xtrans, row + self.ytrans
                    self.GM[tcol, trow].visible = True
                    x = -H_WIDTH + 25 + col * 50
                    self.GM[tcol, trow].position = (x, y)
            for ind in range(len(self.monsters)):
                xm, ym = monstersXY[ind]
                xmt, ymt = xm - 50 * self.xtrans, ym - 50 * self.ytrans
                if (-400 <= xmt <= 400) and (-300 <= ymt <= 200):
                    self.monsters[ind].visible = True
                    self.monsters[ind].position = (xmt, ymt)
                else:
                    self.monsters[ind].visible = False
            if self.Link.x > 400:
                self.Link.x = -800 + self.Link.x
            elif self.Link.x < -400:
                self.Link.x = 800 + self.Link.x
            if self.Link.y > 200:
                self.Link.y = -500 + self.Link.y
            elif self.Link.y < -300:
                self.Link.y = 500 + self.Link.y
            self.toMove = False

    def updateLink(self):
        if self.Link.dx or self.Link.dy:
            num1, num2 = directions[(self.Link.dx, self.Link.dy)]
            num = num1 if self.Link.frame <= 9 else num2
            self.Link.dir = int(num2 // 2) - 1 
            self.Link.frame += 1
            self.Link.frame = self.Link.frame % 20
            self.Link.texture = f"link_{num}"
            cell_x = int((self.Link.y + 250) // 50) + self.ytrans
            cell_y = int((self.Link.x + 400) // 50) + self.xtrans
            ox, oy = self.Link.x, self.Link.y
            self.Link.x += 25 * self.Link.dx
            self.Link.y += 25 * self.Link.dy
            cell_y = int((self.Link.y + 250) // 50) + self.ytrans + 1
            cell_x = int((self.Link.x + 400) // 50) + self.xtrans
            if str(self.GM[cell_x, cell_y].texture) != "ground.png":
                self.Link.x = ox
                self.Link.y = oy
                self.Link.dx = self.Link.dy = 0
            else:
                self.Link.x = ox + 2 * self.Link.dx
                self.Link.y = oy + 2 * self.Link.dy
            if self.Link.x < -400:
                self.xtrans = max(0, self.xtrans - 16)
            elif self.Link.x > 400:
                self.xtrans = min(48, self.xtrans + 16)
            if self.Link.y < -300:
                self.ytrans = max(0, self.ytrans - 10)
            elif self.Link.y > 200:
                self.ytrans = min(10, self.ytrans + 10)
            self.toMove = (not (-400 < self.Link.x < 400) or
                           not (-300 < self.Link.y < 200))
            mx = (400 + 50 * self.xtrans + self.Link.x) / 12.5
            my = (300 + 50 * self.ytrans + self.Link.y) / 12.5            
            self.miniLink.x = self.navigation.lbx + mx 
            self.miniLink.y = self.navigation.lby + my               

    def updateSword(self):
        if self.sword.frame > 0:
            sdx, sdy = self.sword.dx, self.sword.dy
            sdir = 1 if (self.sword.frame > 5) else -1
            self.sword.x += sdir * sdx * 2
            self.sword.y += sdir * sdy * 2
            self.sword.frame -= 1
        else:
            self.sword.visible = False

    def markMonsters(self):
        for Mon in self.monsters:
            if Mon.visible and self.sword.visible:
                sdx, sdy = self.sword.dx, self.sword.dy
                hitinfo = raycast(self.Link.position, Vec3(sdx, -sdy, 0), 
                                  distance=60)
                if hitinfo.hit:
                    if hitinfo.entity == Mon:
                        Mon.state = 9
                        break
        
    def updateMonsters(self):
        self.markMonsters()
        for Mon in self.monsters:
            if Mon.state < 10:
                Mon.rotation_z += 10
                Mon.state -= 1
            if not Mon.state:    
                ind = self.monsters.index(Mon)
                destroy(Mon)
                del self.monsters[ind]
                del monstersXY[ind]
                
    def update(self):
        self.updateGM()
        self.updateLink()
        self.updateSword()
        self.updateMonsters()

game = ZeldaGame()


def input(key):
    game.Link.dx = held_keys['right arrow'] - held_keys['left arrow']
    game.Link.dy = held_keys['up arrow'] - held_keys['down arrow']
    if key == "space":
        game.sword.dx, game.sword.dy = sworddirs[game.Link.dir]
        game.sword.frame = 10
        game.sword.texture = f"sword_{game.Link.dir}"
        game.sword.x = game.Link.x + 30 * game.sword.dx
        game.sword.y = game.Link.y - 35 * game.sword.dy
        game.sword.visible = True


app.run()

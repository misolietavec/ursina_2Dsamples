from ursina import *
from random import randint

NROWS =  10      # numer of brick rows 
NCOLS =  20      # number of brick columns
NCOLORS = 4      # 3 .. 5 is normal
B_WIDTH = 64     # brick width

C_WIDTH =  NCOLS * B_WIDTH
C_HEIGHT = NROWS * B_WIDTH + 100
 

app = Ursina(size=(C_WIDTH, C_HEIGHT), title="SameGame")
window.borderless = False
camera.orthographic = True
camera.fov = C_HEIGHT       # field of vision


cell_colors = {0: color.black, 1: color.green, 2: color.blue, 
               3: color.red, 4: color.yellow, 5: color.magenta}

window.color = cell_colors[0] 

def cell_clicked():
    ent = mouse.hovered_entity
    if ent:
        try:
            col, row = map(int, ent.name.split("_")[1:])
            if not game.alone(col, row):
                game.floodfill(col, row)
                game.fall_all()
        except ValueError:
            pass
        

class SameGame:
    def __init__(self, ncolors=NCOLORS):
        self.ncolors = ncolors
        self.initAttrs()
        self.message = Text(text='Score: 0', scale=2, x=0 , y=-0.43, origin=(0, 0), color=color.white)
        self.quads = None
        self.initBoard()

    def initAttrs(self):
        self.to_fill = set()
        self.score = 0
        self.score_diff = 0
        self.score_corr = 0
        self.empty_cols = []

             
    def initBoard(self):
        self.colors = [[0] * NROWS for col in range(NCOLS)]
        self.quads = [[0] * NROWS for col in range(NCOLS)]
        ycent = (B_WIDTH - C_WIDTH) / 2 
        # store cell centers coordinates and colors, columnwise
        for row in range(NCOLS):
            xcent = (B_WIDTH + 48 - C_HEIGHT) / 2 
            for col in range(NROWS):   
                xcent += B_WIDTH
                qcolor = randint(1, self.ncolors)
                self.colors[row][col] = qcolor
                self.quads[row][col] = Entity(model="quad", collider="box", position=(ycent, xcent), 
                                              color=cell_colors[qcolor], scale = B_WIDTH - 2 , 
                                              name=f"cell_{row}_{col}", on_click=cell_clicked)  
            ycent += B_WIDTH

    def updateBoard(self):
        for row in range(NROWS):
            for col in range(NCOLS):
                self.quads[col][row].color = cell_colors[self.colors[col][row]]
        self.message.text = f'Score: {self.score}'

        if self.endGame():
            if not self.score_corr: 
                self.score_correction()
                self.score_corr = True
            self.compactLeft()
            self.message.text = f"Game Over, Score: {self.score}"
            self.message.color = color.green


    def neighbours(self,i,j):
        possible = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        
        return [p for p in possible if (0 <= p[0] < NCOLS) 
                                   and (0 <= p[1] < NROWS)]
    
    def alone(self,i,j):
        # i -column, j - row
        color = self.colors[i][j]
        res = True
        if color == 0:
            return True
        for k,l in self.neighbours(i,j):
            if self.colors[k][l] == color:
                res = False
                break
        return res        
    
    def floodfill(self, i, j,color=None):        
        if color == None:
            self.to_fill = set()
            if self.colors[i][j]:
                color = self.colors[i][j]
            if self.alone(i,j):
                return 
        if self.colors[i][j] == color:
            self.colors[i][j] = 0
            self.to_fill.add(i)
            self.score_diff += 1
        else:
            return
        for k,l in self.neighbours(i,j):
            self.floodfill(k,l,color=color)

                        
    def compactLeft(self):
        if self.empty_cols == []:
            return 
        for c in sorted(self.empty_cols,reverse=True): 
            for cindex in range(c, NCOLS-1):
                self.colors[cindex] = self.colors[cindex + 1]
            self.colors[NCOLS-1] = [0] * NROWS
        self.empty_cols = []
          
    def fall_all(self):
        if self.to_fill == set():
            self.score_diff = 0
            return
        for col in self.to_fill:
            if sum(self.colors[col]) == 0:
                self.empty_cols.append(col)
                continue
            colored = []
            for row in range(NROWS):
                cc = self.colors[col][row]
                if cc:
                    colored.append(cc)
            new_col = colored + [0] * (NROWS - len(colored))
            self.colors[col] = new_col
        self.compactLeft()
        nscore = self.score_diff - 1    
        self.score += (nscore * nscore)
        self.score_diff = 0
            
    def endGame(self):
        return sum([self.alone(i,j) for i in range(NCOLS) 
                    for j in range(NROWS)]) == NROWS * NCOLS

    def score_correction(self):
        rem = sum(bool(self.colors[c][r]) for c in range(NCOLS) 
                                          for r in range(NROWS)) 
        if rem == 0:
            self.score += 1000
        # else:
        #    self.score -= (rem-1)*(rem-1)

def update():
    game.updateBoard()

def input(key):
    global game
    if key == "q":
        quit()
    if key == "n":
        scene.clear()
        game = SameGame()
    if key in ("3", "4", "5"):
        scene.clear()
        game = SameGame(ncolors=int(key))  
        
game = SameGame()
                 
app.run()

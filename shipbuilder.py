import pygame
from pygame import FULLSCREEN
import random
import time
import math
import copy

#window setup
import ctypes
user32 = ctypes.windll.user32
global scr_width
global scr_height
scr_width = user32.GetSystemMetrics(0)
scr_height = user32.GetSystemMetrics(1)
window = pygame.display.set_mode((scr_width,scr_height),FULLSCREEN)
pygame.display.set_caption("LARCH")
pygame.font.init()
from pygame.locals import *
pygame.init()


#Objects
class Board:
    def __init__(self):
        #gameplay
        self.RUN = True
        self.parts = []
        self.particles = []
        self.credits = 900

        #sounds
        self.ambience = pygame.mixer.Sound("sounds\\ambience.wav")

        #dim
        self.width = 10
        self.height = 15
        self.thickness = 50
        self.coord = [scr_width//2-(self.width*self.thickness//2), scr_height//2-(self.height*self.thickness//2)]

        #left bar
        self.BarWidth = 260
        self.items = [Cockpit(False), Engine(False), Gun(False), Block(False), Corner(False), Concave(False)]
        self.gap = 920 // len(self.items)
        self.BuildmodeTransition()
        

    
    def Show(self):
        #board
        if self.buildmode:
            for x in range(0,self.width):
                for y in range(0, self.height):
                    #outer
                    pygame.draw.rect(window, (40,62,63), (self.coord[0]+(self.thickness*x), self.coord[1]+(self.thickness*y), self.thickness, self.thickness))

                    #inner
                    details = [self.coord[0]+(self.thickness*x)+1, self.coord[1]+(self.thickness*y)+1, self.thickness-2, self.thickness-2]
                    if x == 0:
                        details[0] -= 1
                        details[2] += 1
                    elif x == self.width-1:
                        details[0] += 1
                        details[2] += 1

                    if y == 0:
                        details[1] -= 1
                        details[3] += 1
                    elif y == self.height-1:
                        details[1] += 1
                        details[3] += 1 

                    pygame.draw.rect(window, (33,44,48), details)
            
            #leftbar=======
            pygame.draw.rect(window, (40,62,63), (0, 0, self.BarWidth, scr_height))
            #highlights
            M.highlight = -1
            for i in self.showcase:
                if (i[0] < M.coord[0] < i[0] + self.BarWidth) and (i[1] < M.coord[1] < i[1] + self.gap):
                    M.highlight = self.showcase.index(i)
                    pygame.draw.rect(window, (60,82,83), (i[0], i[1], self.BarWidth, self.gap))

                    #prices
                    item = self.items[M.highlight]
                    PrcFont = pygame.font.SysFont('', 25)
                    Text = PrcFont.render(str(item.cost), False, (247,216,148))
                    window.blit(Text, (item.coord[0]-10, item.coord[1]+50))

            

            #Credits
            SubFont = pygame.font.SysFont('', 100)
            Text = SubFont.render("CR "+str(self.credits), False, (247,216,148))
            #pygame.draw.rect(window, (60,82,83), (0, 0, self.BarWidth, 100))
            window.blit(Text,(10,10))

        #signature
        SigFont = pygame.font.SysFont('', 25)
        Text = SigFont.render(("BY RICHARD BURGIN"), False, (247,216,148))
        window.blit(Text,(30,scr_height-50))

        #ambience
        if not pygame.mixer.get_busy():
            pygame.mixer.Sound.play(self.ambience)

    def FlightTransition(self):
        self.buildmode = False

        for i in self.items:
            self.parts.remove(i)
        
    
    def BuildmodeTransition(self):
        self.buildmode = True

        #left bar
        self.showcase = []
        #items
        for i in self.items:
            self.parts.append(i)
            if len(self.showcase) < 1:
                x, y = 0, 100
            else:
                x, y = self.showcase[-1][0], self.showcase[-1][1] + self.gap
            i.coord = [x+self.BarWidth//2 , y+self.gap//2]
            self.showcase.append([x , y])



class Part:
    def __init__(self, held):
        #details
        self.held = held
        self.pycoord = [False,False]
        self.coord = copy.deepcopy(M.coord)

        #differentiate later===========
        self.deg = 0
        self.cost = 50
        self.m = 10

        #image
        self.width = self.image.get_height()
        self.height = self.image.get_width()

        #sound
        self.liftsound = pygame.mixer.Sound("sounds\lift.wav")

    def Show(self):
        if self.held:
            self.coord = copy.deepcopy(M.coord)
        blit = [self.coord[0]-self.width//2, self.coord[1]-self.height//2]
        window.blit(self.image, blit)
    
    def Drop(self, pycoord):
        self.held = False
        self.pycoord = pycoord
        self.coord = [B.coord[0] + pycoord[0]*B.thickness+B.thickness//2, B.coord[1] + pycoord[1]*B.thickness+B.thickness//2]

        #sound
        pygame.mixer.Sound.play(random.choice(self.dropsound))
    
    def Lift(self):
        self.held = True
        self.pycoord = [False,False]
        self.coord = copy.deepcopy(M.coord)

class Hull(Part):
    def __init__(self, held):
        #sound
        self.dropsound = []
        for i in range(1,4):
            self.dropsound.append(pygame.mixer.Sound("sounds\hull#"+str(i)+".wav"))

        super().__init__(held)

class Block(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\1x1.png")

        super().__init__(held)

class Corner(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\corner.png")

        super().__init__(held)
        self.cost = 25

class Concave(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\concave.png")

        super().__init__(held)
        self.cost = 25

class Cockpit(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\cockpit.png")

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\cockpit.wav")]

        super().__init__(held)
        

class Engine(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\engine.png")

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\engine.wav")]

        super().__init__(held)

class Gun(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\gun.png")

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\gun.wav")]

        super().__init__(held)
        

#class Shield(Part):
#    def __init__(self, held):
#        #image
#        self.image = pygame.image.load("images\\1x1.png")
#
#        super().__init__(held)


class Particle:
    def __init__(self, coord, colour, vel):
        self.coord = copy.deepcopy(coord)
        self.deg = random.randint(0, 360)
        self.vel = random.uniform(1, vel)
        self.colour = colour

    def Show(self):
        rad = math.radians(self.deg)
        opp = self.vel * math.sin(rad)
        adj = self.vel * math.cos(rad)

        self.coord[0] += opp
        self.coord[1] += adj

        pygame.draw.circle(window, self.colour, (int(self.coord[0]), int(self.coord[1])), int(self.vel), 0)

        #entropy
        if random.choice([True,False]):
            self.deg += random.randint(-10,10)
        self.vel -= .1
        if self.vel <= 0:
            B.particles.remove(self)

class Mouse:
    def __init__(self):
        self.coord = ["",""]
        self.pycoord = [0,0]
        self.coord[0], self.coord[1] = pygame.mouse.get_pos()
        self.found = False
        self.selected = False
        self.highlight = -1

    def Input(self):
        for event in pygame.event.get():
            if B.buildmode:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.ClickDOWN()
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.selected!= False:
                        self.ClickUP()
            if event.type == pygame.MOUSEMOTION:
                self.coord[0], self.coord[1] = pygame.mouse.get_pos()
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DELETE]:
                    self.Delete()
                if self.selected != False:
                    if keys[pygame.K_LEFT]:
                        self.selected.image = pygame.transform.rotate(self.selected.image, 90)
                        self.selected.deg += 90
                    if keys[pygame.K_RIGHT]:
                        self.selected.image = pygame.transform.rotate(self.selected.image, -90)
                        self.selected.deg -= 90
                if keys[pygame.K_SPACE]:
                    if B.buildmode:
                        B.FlightTransition()
                    else:
                        B.BuildmodeTransition()

    def Coordfinder(self):
        #finds coords on board
        self.found = False
        xFound = False
        yFound = False
        X = 0
        Y = 0
        for x in range(0, B.width):
            if (xFound == False) and (self.coord[0] >= (B.coord[0] + B.thickness*x)) and (self.coord[0] <= (B.coord[0] + B.thickness*(x+1))):
                X = x
                xFound = True
            for y in range(0, B.height):
                if (yFound == False) and (self.coord[1] >= B.coord[1] + B.thickness*y) and (self.coord[1] <= B.coord[1] + B.thickness*(y+1)):
                    Y = y
                    yFound = True

        if xFound and yFound:
            self.found = True
            self.pycoord = [X, Y]

    def ClickDOWN(self):
        self.Coordfinder()
        #exit
        if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
            B.RUN = False

        #effects
        for i in range(0,25):
            B.particles.append(Particle(self.coord, (214,245,246), 3))

        #generate
        if self.found:
            for i in B.parts:
                if i.pycoord == self.pycoord:
                    i.Lift()
                    self.selected = i
                    break 
        elif B.credits > 0:
            #left bar
            if self.highlight == 0:
                B.parts.append(Cockpit(True))
                self.selected = B.parts[-1]
            elif self.highlight == 1:
                B.parts.append(Engine(True))
                self.selected = B.parts[-1]
            elif self.highlight == 2:
                B.parts.append(Gun(True))
                self.selected = B.parts[-1]
            elif self.highlight == 3:
                B.parts.append(Block(True))
                self.selected = B.parts[-1]
            elif self.highlight == 4:
                B.parts.append(Corner(True))
                self.selected = B.parts[-1]
            elif self.highlight == 5:
                B.parts.append(Concave(True))
                self.selected = B.parts[-1]
            
            #credits + sound
            if self.selected != False:
                #credits
                B.credits -= self.selected.cost
                if B.credits < 0:
                    B.credits = 0
                
                #sound
                pygame.mixer.Sound.play(self.selected.liftsound)
            

    def ClickUP(self):
        self.Coordfinder()

        if self.found:
            #occupied
            occupied = False
            for i in B.parts:
                if i.pycoord == self.pycoord:
                    occupied = True
                    break
            
            #verdict
            if occupied:
                B.parts.remove(self.selected)
            else:
                self.selected.Drop(copy.deepcopy(self.pycoord))
        else:
            B.credits += self.selected.cost
            B.parts.remove(self.selected)

        self.selected = False
                
    def Delete(self):
        self.Coordfinder()

        #scan
        for i in B.parts:
            if i.pycoord == self.pycoord:
                #effects
                for p in range(0,50):
                    B.particles.append(Particle(i.coord, (116,116,116), 5))

                B.credits += i.cost
                B.parts.remove(i)
                break


M = Mouse()
B = Board()


while B.RUN:
    pygame.time.delay(1)
    window.fill((33,44,48))

    M.Input()
    B.Show()

    for i in B.parts:
        i.Show()
    for i in B.particles:
        i.Show()


    
    pygame.display.update()
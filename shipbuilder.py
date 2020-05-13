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
        self.ships = []
        self.parts = []
        self.particles = []
        self.credits = 900

        #sounds
        self.ambience = pygame.mixer.Sound("sounds\\ambience.wav")

        #dim
        self.width = 11
        self.height = 15
        self.thickness = 50
        self.coord = [scr_width//2-(self.width*self.thickness//2), scr_height//2-(self.height*self.thickness//2)]

        #limit
        self.CPlimit = 1

        #left bar
        self.BarWidth = 260
        self.items = [Cockpit(False), Engine(False), Cannon(False), Block(False), Corner(False), Concave(False), Convex(False)]
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

                    #prices + limit
                    item = self.items[M.highlight]
                    PrcFont = pygame.font.SysFont('', 25)
                    #limit
                    if self.showcase.index(i) == 0:
                        Text = PrcFont.render("MAX 1", False, (247,216,148))
                        window.blit(Text, (item.coord[0]-23, item.coord[1]-60))
                    #prices
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

    def ConnectedScan(self):
        result = True
        ticker = [[0,-1],[1,0],[0,1],[-1,0]]
        for i in self.parts:
            bind = False
            for x in ticker:
                for p in self.parts:
                    if i.pycoord[0]+x[0] == p.pycoord[0]:
                        if i.pycoord[1]+x[1] == p.pycoord[1]:
                            bind = True
                            break
                if bind:
                    break
            if not bind:
                result = False
        
        return result

    def FlightTransition(self):
        self.buildmode = False
        if M.selected != False:
            B.credits += M.selected.cost
            if M.selected.CP:
                B.CPlimit += 1
            B.parts.remove(M.selected)
        for i in self.items:
            self.parts.remove(i)

        #cockpit check
        seat = False
        for i in self.parts:
            if i.CP:
                seat = True
                break
        if not seat:
            self.BuildmodeTransition()

        #connected check
        if not self.ConnectedScan():
            self.BuildmodeTransition()
        
        #empty check
        if len(self.parts) == 0:
            self.BuildmodeTransition()
         
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

class Ship:
    def __init__(self):
        #suvat
        self.F = [0,0] 
        self.u = [0,0]
        self.a = [0,0]
        self.s = [0,0]

        #other variables
        self.deg = 0

        #find CP
        for i in B.parts:
            if i.CP:
                self.coord = copy.deepcopy(i.coord)

        #accumulate thrust
        self.strength = 0
        for i in B.parts:
            if i.CP == "engine":
                self.strength += 1

        #acumulate mass
        self.m = 0
        for i in B.parts:
            self.m += i.m
            if i.CP:
                self.coord = copy.deepcopy(i.coord)

        #engine
        self.on = pygame.image.load("images\engine_on.png")
        self.off = pygame.image.load("images\engine_off.png")

    def Calculate(self):
        #self.BoundaryCheck()
        Resultant_F = []
        #find resultant force in axis (F=ma)
        Resultant_F.append(self.F[0]) 
        Resultant_F.append(self.F[1])

        for i in range (0,2):
            #find acceleration on axis
            self.a[i] = 0
            if Resultant_F[i] != 0:
                self.a[i] =  Resultant_F[i] / self.m

            #find displacement on axis (s = ut- 1/2 at^2)
            self.s[i] = self.u[i] - 0.5*self.a[i]

        #displace
        self.coord[0] -= self.s[0]
        self.coord[1] += self.s[1]

    def Reset(self):
        #find velocity used in next Calculate (v = u + at)
        for i in range (0,2):
            self.u[i] = self.u[i] + self.a[i]
            self.u[i] *= 0.996

            #reset values
            self.F[i] = 0
        
        #reset engine image
        for i in B.parts:
            if i.image == self.on:
                i.image = self.off

    def Active(self):
        #show engines on
        for i in B.parts:
            if i.image == self.on:
                i.image = self.off

        thrust = self.strength

        #pythagoras
        radians = math.radians(self.deg)
        opp = thrust * math.sin(radians)
        adj = thrust * math.cos(radians)
        self.F[0] = -opp
        self.F[1] = adj

    def Turn(self, left):
        if left:
            change = 2
        else:
            change = -2

        self.deg += change

        for i in B.parts:
            i.flightdeg += change


class Part:
    def __init__(self, held):
        #details
        self.held = held
        self.pycoord = [False,False]
        self.coord = copy.deepcopy(M.coord)

        #gameplay
        self.flightdeg = 0
        self.deg = 0
        self.cost = 50
        self.m = 10
        self.health = 10
        self.CP = False

        #image
        self.blitimage = pygame.transform.rotate(self.image, self.deg)
        self.width = self.image.get_height()
        self.height = self.image.get_width()

        #sound
        self.liftsound = pygame.mixer.Sound("sounds\lift.wav")

    def BuildShow(self):
        if self.held:
            self.coord = copy.deepcopy(M.coord)
        blit = [self.coord[0]-self.width//2, self.coord[1]-self.height//2]
        window.blit(self.image, blit)

    def FlightShow(self):
        #dim
        self.width = self.blitimage.get_width()
        self.height = self.blitimage.get_height()

        #blit
        self.blitimage = pygame.transform.rotate(self.image, self.flightdeg)
        blit = [self.coord[0] - self.width//2,self.coord[1] - self.height//2]

        #write
        window.blit(self.blitimage,(blit[0] , blit[1]))
    
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


class Cockpit(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\cockpit.png")

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\cockpit.wav")]

        super().__init__(held)
        
        #gameplay
        self.CP = True
        self.deg = 1

class Engine(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\engine_off.png")

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\engine.wav")]

        super().__init__(held)
        self.CP = "engine"


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

        #gameplay
        self.deg = 1

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

class Convex(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\convex.png")

        super().__init__(held)
        self.cost = 25


class Gun(Part):
    def __init__(self, held):
        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\gun.wav")]

        super().__init__(held)

class Cannon(Gun):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\cannon.png")

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

    def BuildInput(self):
        for event in pygame.event.get():
            #mouse
            if event.type == pygame.MOUSEMOTION:
                self.coord[0], self.coord[1] = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.BuildClickDOWN()
            if event.type == pygame.MOUSEBUTTONUP:
                if self.selected!= False:
                    self.BuildClickUP()

            #keys
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DELETE]:
                    self.Delete()
                if self.selected != False:
                    if self.selected.deg != 1:
                        if keys[pygame.K_LEFT]:
                            self.selected.image = pygame.transform.rotate(self.selected.image, 90)
                            self.selected.deg += 90
                        if keys[pygame.K_RIGHT]:
                            self.selected.image = pygame.transform.rotate(self.selected.image, -90)
                            self.selected.deg -= 90
                if keys[pygame.K_SPACE]:
                    B.FlightTransition()
    
    def FlightInput(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            #mouse
            if event.type == pygame.MOUSEMOTION:
                self.coord[0], self.coord[1] = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.FlightClickDOWN()

            #key
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    B.BuildmodeTransition()
        if keys[pygame.K_w]:
            #S.Active()
            pass
        if keys[pygame.K_a]:
            S.Turn(True)
        if keys[pygame.K_d]:
            S.Turn(False)

    def FlightClickDOWN(self):
        #exit
        if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
            B.RUN = False

        #effects
        for i in range(0,25):
            B.particles.append(Particle(self.coord, (214,245,246), 3))

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

    def BuildClickDOWN(self):
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
                if B.CPlimit > 0:
                    B.parts.append(Cockpit(True))
                    self.selected = B.parts[-1]
                    B.CPlimit -= 1
            elif self.highlight == 1:
                B.parts.append(Engine(True))
                self.selected = B.parts[-1]
            elif self.highlight == 2:
                B.parts.append(Cannon(True))
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
            elif self.highlight == 6:
                B.parts.append(Convex(True))
                self.selected = B.parts[-1]
            
            #credits + sound
            if self.selected != False:
                #credits
                B.credits -= self.selected.cost
                if B.credits < 0:
                    B.credits = 0
                
                #sound
                pygame.mixer.Sound.play(self.selected.liftsound)
            
    def BuildClickUP(self):
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
                B.credits += self.selected.cost
                if self.selected.CP:
                    B.CPlimit += 1
                B.parts.remove(self.selected)
            else:
                self.selected.Drop(copy.deepcopy(self.pycoord))
        else:
            B.credits += self.selected.cost
            if self.selected.CP:
                B.CPlimit += 1
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
                if i.CP:
                    B.CPlimit += 1
                B.parts.remove(i)
                break


M = Mouse()
B = Board()
S = Ship()

while B.RUN:
    pygame.time.delay(1)
    window.fill((33,44,48))

    if B.buildmode:
        M.BuildInput()
    else:
        M.FlightInput()
    B.Show()
    
    if B.buildmode: 
        for i in B.parts:
            i.BuildShow()
    else:
        for i in B.parts:
            i.FlightShow()
    for i in B.particles:
        i.Show()


    
    pygame.display.update()
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
        self.projectiles = []
        self.credits = 1000

        #sounds
        self.ambience = pygame.mixer.Sound("sounds\\ambience.wav")

        #dim
        self.width = 11
        self.height = 15
        self.thickness = 50
        self.coord = [scr_width//2-(self.width*self.thickness//2), scr_height//2-(self.height*self.thickness//2)]

        #left bar
        self.BarWidth = 300
        self.items = [Engine(False), Cannon(False), Shield(False), Gyro(False), Block(False), Corner(False), Concave(False), Convex(False)]
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
                    if item.cost > 99:
                        window.blit(Text, (item.coord[0]-15, item.coord[1]+30))
                    else:
                        window.blit(Text, (item.coord[0]-10, item.coord[1]+30))

            

            #Credits
            SubFont = pygame.font.SysFont('', 100)
            Text = SubFont.render("CR "+str(self.credits), False, (247,216,148))
            pygame.draw.rect(window, (60,82,83), (0, 0, self.BarWidth, 100))
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
                            if i.allow[ticker.index(x)]:
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
            B.parts.remove(M.selected)
        for i in self.items:
            self.parts.remove(i)
            
        #connected check
        if not self.ConnectedScan():
            self.BuildmodeTransition()
        
        #empty check
        if len(self.parts) == 0:
            self.BuildmodeTransition()

        #parts
        for i in self.parts:
            if i.sig == "cockpit":
                CP = i
        for i in self.parts:
            #hypotenuse
            x = i.coord[0] - CP.coord[0] #x is positive when part is to the right of CP
            y = i.coord[1] - CP.coord[1] #y is positive when part is below CP
            i.hypotenuse = math.sqrt(x**2 + y**2)

            #flightdeg
            i.flightdeg = 0
            if i.hypotenuse != 0 and x != 0 and y != 0:
                #for any diagonals
                trig = math.degrees(math.asin(x/i.hypotenuse))

                orient = round(trig)
                if y > 0:
                    i.flightdeg += trig
                else:
                    if orient > 0:
                        i.flightdeg += 90 - trig
                    elif orient < 0:
                        i.flightdeg += -90 - trig
                if y < 0: 
                    if orient > 0:
                        i.flightdeg += 90
                    elif orient < 0:
                        i.flightdeg -= 90
                
            else:
                #for axes
                if x > 0:
                    i.flightdeg += 90
                elif x < 0:
                    i.flightdeg += -90
                elif y < 0:
                    i.flightdeg += 180

            #flightcoord
            i.flightcoord = copy.deepcopy(i.coord)
        
        #ship
        global S
        S = Ship()

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
            if i.sig == "cockpit":
                self.coord = copy.deepcopy(i.coord)

        #accumulate values
        self.turnspeed = 0
        self.strength = 0
        self.m = 0
        self.shield = 0
        for i in B.parts:
            self.m += i.m #mass

            if i.sig == "gyro": #turn speed
                self.turnspeed += 1

            if i.sig == "engine": #thrust
                self.strength -= 5

            if i.sig == "cockpit": #coord
                self.coord = copy.deepcopy(i.coord)

            if i.sig == "shield": #shield
                self.shield += 1

        #engine
        self.on = pygame.image.load("images\\engine_on.png")
        self.off = pygame.image.load("images\\engine_off.png")

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
        for i in B.parts:
            i.flightcoord[0] -= self.s[0]
            i.flightcoord[1] += self.s[1]

    def Reset(self):
        #find velocity used in next Calculate (v = u + at)
        for i in range (0,2):
            self.u[i] = self.u[i] + self.a[i]
            self.u[i] *= 0.996

            #reset values
            self.F[i] = 0
        
        #reset engine image
        for i in B.parts:
            if i.sig == "engine":
                i.image = self.off

    def Active(self):
        #show engines on
        for i in B.parts:
            if i.sig == "engine":
                i.image = self.on

        thrust = self.strength

        #pythagoras
        radians = math.radians(self.deg)
        opp = thrust * math.sin(radians)
        adj = thrust * math.cos(radians)
        self.F[0] = -opp
        self.F[1] = adj

    def Turn(self, left):
        if left:
            change = self.turnspeed
        else:
            change = -self.turnspeed

        self.deg += change

        for i in B.parts:
            if i.sig != "cockpit":
                i.flightdeg += change
                i.Displace()


class Part:
    def __init__(self, held):
        #details
        self.held = held
        self.pycoord = [False,False]
        self.coord = copy.deepcopy(M.coord)
        self.flightcoord = [0,0]

        #for ship displacement
        self.hypotenuse = False

        #gameplay
        self.flightdeg = 0
        self.deg = 0
        self.cost = 50
        self.m = 10
        self.health = 10
        self.sig = False
        self.allow = [True, True, True, True] #starts top, cycles clockwise

        #image
        self.blitimage = pygame.transform.rotate(self.image, self.deg)
        self.width = self.image.get_height()
        self.height = self.image.get_width()

        #sound
        self.liftsound = pygame.mixer.Sound("sounds\\lift.wav")

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
        self.blitimage = pygame.transform.rotate(self.image, S.deg)
        blit = [self.flightcoord[0] - self.width//2,self.flightcoord[1] - self.height//2]

        #write
        window.blit(self.blitimage,(blit[0] , blit[1]))

    def Displace(self):
        rad = math.radians(self.flightdeg)
        y = S.coord[1] + self.hypotenuse*math.cos(rad)
        x = S.coord[0] + self.hypotenuse*math.sin(rad)

        self.flightcoord = [x,y]
    
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
        self.image = pygame.image.load("images\\cockpit.png")

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\\cockpit.wav")]

        super().__init__(held)
        
        #gameplay
        self.sig = "cockpit"

class Engine(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\engine_off.png")

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\\engine.wav")]

        super().__init__(held)
        
        #gameplay
        self.deg = 1
        self.sig = "engine"
        self.allow = [True, False, False, False]

class Shield(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\shield_on.png")

        #sounds
        self.dropsound = [pygame.mixer.Sound("sounds\\shield_regen.wav")]

        super().__init__(held)

        #gameplay
        self.cost = 200
        self.m = 50
        self.sig = "shield"
        self.deg = 1

class Gyro(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\gyro.png")

        #sounds
        self.dropsound = [pygame.mixer.Sound("sounds\\gyro.wav")]

        super().__init__(held)

        #gameplay
        self.sig = "gyro"
        self.deg = 1


class Hull(Part):
    def __init__(self, held):
        #sound
        self.dropsound = []
        for i in range(1,4):
            self.dropsound.append(pygame.mixer.Sound("sounds\\hull#"+str(i)+".wav"))

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
        self.image = pygame.image.load("images\\corner.png")

        super().__init__(held)

        #gameplay
        self.cost = 25
        self.allow = [False, False, True, True]

class Concave(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\concave.png")

        super().__init__(held)

        #gameplay
        self.cost = 25
        self.allow = [False, True, True, True]

class Convex(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\convex.png")

        super().__init__(held)

        #gameplay
        self.cost = 25
        self.allow = [False, False, True, False]


class Gun(Part):
    def __init__(self, held):
        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\\gun.wav")]

        super().__init__(held)

        #gameplay
        self.sig = "gun"
        self.cost = 100
        self.allow = [False, False, True, False]

    def Fire(self):
        for i in range(0,10):
            B.particles.append(Particle(self.flightcoord, (214,245,246), 10))
            B.particles[-1].deg = S.deg - 180 + self.deg

class Cannon(Gun):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\cannon.png")

        super().__init__(held)


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
                if keys[pygame.K_f]:
                    self.Delete()
                if self.selected != False:
                    if self.selected.deg != 1:
                        if keys[pygame.K_a]:
                            self.Rotate(True)
                        if keys[pygame.K_d]:
                            self.Rotate(False)
                if keys[pygame.K_q]:
                    B.FlightTransition()

    def Rotate(self, left):
        if left:
            change = 90
        else:
            change = -90

        #rotates image
        self.selected.image = pygame.transform.rotate(self.selected.image, change)
        self.selected.deg += change

        #cycles allow
        if left:
            front = self.selected.allow[0]
            self.selected.allow.pop(0)
            self.selected.allow.append(front)
        else:
            back = self.selected.allow[-1]
            self.selected.allow.pop(-1)
            self.selected.allow.insert(0,back)
    
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
                if keys[pygame.K_q]:
                    B.BuildmodeTransition()
        if keys[pygame.K_w]:
            S.Active()
        if keys[pygame.K_a]:
            S.Turn(True)
        if keys[pygame.K_d]:
            S.Turn(False)
        if keys[pygame.K_SPACE]:
            for i in B.parts:
                if i.sig == "gun":
                    i.Fire()

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
                if i.pycoord == self.pycoord and i.sig != "cockpit":
                    i.Lift()
                    self.selected = i
                    break 
        elif B.credits > 0:
            #left bar
            if self.highlight == 0:
                B.parts.append(Engine(True))
                self.selected = B.parts[-1]
            elif self.highlight == 1:
                B.parts.append(Cannon(True))
                self.selected = B.parts[-1]
            elif self.highlight == 2:
                B.parts.append(Shield(True))
                self.selected = B.parts[-1]
            elif self.highlight == 3:
                B.parts.append(Gyro(True))
                self.selected = B.parts[-1]
            elif self.highlight == 4:
                B.parts.append(Block(True))
                self.selected = B.parts[-1]
            elif self.highlight == 5:
                B.parts.append(Corner(True))
                self.selected = B.parts[-1]
            elif self.highlight == 6:
                B.parts.append(Concave(True))
                self.selected = B.parts[-1]
            elif self.highlight == 7:
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
            if i.pycoord == self.pycoord and i.sig != "cockpit":
                #effects
                for p in range(0,50):
                    B.particles.append(Particle(i.coord, (116,116,116), 5))

                B.credits += i.cost
                B.parts.remove(i)
                break


M = Mouse()
B = Board()

#cockpit
B.parts.append(Cockpit(False))
B.parts[-1].Drop([B.width//2, B.height//2])

while B.RUN:
    pygame.time.delay(1)
    window.fill((33,44,48))

    #input
    if B.buildmode:
        M.BuildInput()
    else:
        M.FlightInput()
    
    #calc
    if not B.buildmode:
        S.Calculate()
    
    #show
    B.Show()
    if B.buildmode: 
        for i in B.parts:
            i.BuildShow()
    else:
        for i in B.parts:
            i.FlightShow()
    for i in B.particles:
        i.Show()

    #reset
    if not B.buildmode:
        S.Reset()
    
    pygame.display.update()
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
        self.stars = []
        self.particlesabove = []
        self.particlesbelow = []
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

        #options
        save = [scr_width-200, 0, 200, 100]
        load = [scr_width-200, 100, 200, 100]
        self.options = [save,load]
        self.optionstitles = ["SAVE", "LOAD"]
        self.optionsinput = False
        self.textboxtext = ""

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

            #options=======
            #rectangle
            for i in self.options:
                pygame.draw.rect(window, (40,62,63), (i))
                if (i[0] < M.coord[0] < i[0] + i[2]) and (i[1] < M.coord[1] < i[1] + i[3]):
                    M.highlight = -self.options.index(i)-2
                    pygame.draw.rect(window, (60,82,83), (i))
                #text
                OpFont = pygame.font.SysFont('', 25)
                Text = OpFont.render(self.optionstitles[self.options.index(i)], False, (247,216,148))
                window.blit(Text, (i[0]+i[2]//2-10, i[1]+i[3]//2))
            
            #texbox
            if self.optionsinput:
                #line
                l = self.options[-1]
                pygame.draw.line(window, (247,216,148), (l[0], l[1]+l[3]+25), (l[0]+l[2], l[1]+l[3]+25))

                #text
                BoxFont = pygame.font.SysFont('', 20)
                Text = OpFont.render(self.textboxtext, False, (247,216,148))
                window.blit(Text, (self.options[-1][0], self.options[-1][1] + self.options[-1][3]))

            #Credits
            SubFont = pygame.font.SysFont('', 100)
            Text = SubFont.render("CR "+str(self.credits), False, (247,216,148))
            pygame.draw.rect(window, (60,82,83), (0, 0, self.BarWidth, 100))
            window.blit(Text,(10,10))

        else:
            #arena
            pygame.draw.circle(window, (214,245,246), (int(self.arenacoord[0]), int(self.arenacoord[1])), int(self.arenaradius), 10)
            for i in self.stars:
                i.Show()

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

        #arena check
        self.GenArena()
        for i in self.stars:
            i.ArenaCheck()

    def BuildmodeTransition(self):
        self.buildmode = True
        self.arenacoord = [scr_width//2, scr_height//2]

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

    def GenArena(self):
        #arena
        self.stars = []
        self.arenacoord = [scr_width//2, scr_height//2]
        self.arenaradius = 3000
        ticker = [[-1,1],[1,-1],[-1,-1],[1,1]]
        for x in range(0,10):
            for y in range(0,10):
                for i in ticker:
                    X, Y = self.arenacoord[0]+i[0]*x*300, self.arenacoord[1]+i[1]*y*300
                    self.stars.append(Star([X, Y]))

    def Textbox(self):
        act = False
        for event in pygame.event.get():
            #keys
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    act = True
                elif keys[pygame.K_BACKSPACE]:
                    self.textboxtext = self.textboxtext[:-1]
                else:
                    self.textboxtext+= event.unicode

        #save + load
        if act:
            if self.optionsinput == "save":
                self.Save(self.textboxtext)
            elif self.optionsinput == "load":
                self.Load(self.textboxtext)
            self.optionsinput = False

    def Load(self, name):
        self.parts = []
        #adds left bar
        for i in self.items:
            self.parts.append(i)

        #adds cockpit
        B.parts.append(Cockpit(False))
        B.parts[-1].Drop([B.width//2, B.height//2])
        try:
            f = open(name+".txt", "r")

            #cycles the data
            signatures = ["engine", "gun", "shield", "gyro", "block", "corner", "concave", "convex"]

            for line in f:
                items = [Engine(False), Cannon(False), Shield(False), Gyro(False), Block(False), Corner(False), Concave(False), Convex(False)]
                chunks = line.split(",")

                x = signatures.index(chunks[0])

                #new part
                self.parts.append(items[x])
                self.parts[-1].Drop([int(chunks[1]), int(chunks[2])])
                self.parts[-1].deg = int(chunks[3])
                #rotates image
                if self.parts[-1].deg != 1:
                    self.parts[-1].image = pygame.transform.rotate(self.parts[-1].image, self.parts[-1].deg)

            f.close()
        except:
            FileNotFoundError

    def Save(self, name):
        #removes left bar
        for i in self.items:
            self.parts.remove(i)
        
        #removes cockpit
        for i in self.parts:
            if i.sig == "cockpit":
                self.parts.remove(i)
                break

        f = open(name+".txt", "w")
        
        for i in self.parts:
            f.write(i.sig+","+str(i.pycoord[0])+","+str(i.pycoord[1])+","+str(i.deg)+"\n")

        f.close()

        #adds left bar
        for i in self.items:
            self.parts.append(i)

        #adds cockpit
        B.parts.append(Cockpit(False))
        B.parts[-1].Drop([B.width//2, B.height//2])

    

class Entity:
    def __init__(self):
        #suvat
        self.F = [0,0]
        self.u = [0,0]
        self.a = [0,0]
        self.s = [0,0]

        #other variables
        self.deg = 0
        self.hypotenuse = 0

    def Calculate(self):
        self.BoundaryCheck()
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

        self.Displace()

class Projectile(Entity):
    def __init__(self, coord, u, deg):
        #inheritance
        super().__init__()
        self.u = u
        self.deg = deg

        #images
        self.coord = coord
        self.image = pygame.image.load("images\\projectile.png")
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(self.coord[0],self.coord[1],self.width,self.height)

        #gameplay
        self.m = 5
        self.Launch()
        self.delay = 10
    
    def Launch(self):
        self.strength = 100

        #pythagoras
        radians = math.radians(self.deg)
        opp = self.strength * math.sin(radians)
        adj = self.strength * math.cos(radians)
        self.F[0] = -opp
        self.F[1] = adj

    def Show(self):
        #delete slow projectiles
        if self.delay > 0:
            self.delay -= 1
        elif self.u[0] < 1 and self.u[1] < 1 and self.u[0] > -1 and self.u[1] > -1:
            B.projectiles.remove(self)

        #blit
        blitimage = pygame.transform.rotate(self.image, self.deg)
        self.width = blitimage.get_width()
        self.height = blitimage.get_height()
        blit = [self.coord[0] - self.width//2,self.coord[1] - self.height//2]

        #rect
        self.rect = pygame.Rect(self.coord[0],self.coord[1],self.width,self.height)

        #write
        window.blit(blitimage,(blit[0] , blit[1]))

    def Displace(self):
        self.coord[0] -= self.s[0]
        self.coord[1] += self.s[1]
    
    def Reset(self):
        #find velocity used in next Calculate (v = u + at)
        for i in range (0,2):
            self.u[i] = self.u[i] + self.a[i]
            self.u[i] *= 0.996

            #reset values
            self.F[i] = 0

    def BoundaryCheck(self):
        x = self.coord[0] - B.arenacoord[0] 
        y = self.coord[1] - B.arenacoord[1] 
        self.hypotenuse = math.sqrt(x**2 + y**2)

        if self.hypotenuse > B.arenaradius:
            B.projectiles.remove(self)

    def Impact(self):
        for i in B.parts:
            if self.rect.colliderect(i.rect) and self.delay <= 0:
                if S.shield > 0:
                    pygame.mixer.Sound.play(i.brek)
                    S.shield -= 1
                    S.shielddelay = 200
                else:
                    i.health -= 1
                    if i.health <= 0:
                        i.image = i.dead
                for i in range(0,2):
                    #finds momentum
                    self.p = self.m * self.u[i]
                    S_p = S.m * S.u[i]
                    #combines momentum
                    totalp = self.p + S_p
                    #finds u
                    S.u[i] = totalp / S.m
                B.projectiles.remove(self)

class Ship(Entity):
    def __init__(self):
        #inheritance
        super().__init__()

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

        #gameplay
        self.jumpdelay = 0
        self.firedelay = 0
        self.reload = 10

    def Displace(self):
        B.arenacoord[0] += self.s[0]
        B.arenacoord[1] -= self.s[1]
        for i in B.stars:
            i.coord[0] += self.s[0]
            i.coord[1] -= self.s[1]
        for i in B.particlesbelow:
            i.coord[0] += self.s[0]
            i.coord[1] -= self.s[1]
        for i in B.projectiles:
            i.coord[0] += self.s[0]
            i.coord[1] -= self.s[1]

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
                for x in range(0,3):
                    B.particlesbelow.append(Particle(i.flightcoord, (214,245,246), 10, False))
                    B.particlesbelow[-1].deg = S.deg + i.deg + random.randint(-50,50)

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

    def BoundaryCheck(self):
        x = self.coord[0] - B.arenacoord[0] 
        y = self.coord[1] - B.arenacoord[1] 
        self.hypotenuse = math.sqrt(x**2 + y**2)

        if self.hypotenuse > B.arenaradius:
            for i in range(0, 2):
                self.u[i] = -self.u[i]
                self.a[i] = -self.a[i]

    def Jump(self):
        for i in B.parts:
            for x in range(0, 5 -self.jumpdelay//10):
                deg = S.deg + random.randint(-50,50)
                radians = math.radians(deg)
                opp = 30 * math.sin(radians)
                adj = 30 * math.cos(radians)
                coord = [i.flightcoord[0]- opp, i.flightcoord[1]- adj] 
                B.particlesabove.append(Particle(coord, (214,245,246), 50 -self.jumpdelay, True))
                B.particlesabove[-1].deg = deg
        self.jumpdelay -= 1

        #arena check
        B.GenArena()
        for i in B.stars:
            i.ArenaCheck()

class Enemy(Entity):
    def __init__(self):
        pass
    def Ai(self):
        pass

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
        self.health = 3
        self.allow = [True, True, True, True] #starts top, cycles clockwise
        
        #image
        self.dead = pygame.image.load("images\\dead.png")
        self.blitimage = pygame.transform.rotate(self.image, self.deg)
        self.width = self.image.get_height()
        self.height = self.image.get_width()

        #rect
        self.rect = pygame.Rect(self.coord[0],self.coord[1],self.width,self.height)

        #sound
        self.liftsound = pygame.mixer.Sound("sounds\\lift.wav")

    def BuildShow(self):
        if self.held:
            self.coord = copy.deepcopy(M.coord)
        blit = [self.coord[0]-self.width//2, self.coord[1]-self.height//2]
        window.blit(self.image, blit)

    def FlightShow(self):
        #blit
        blitimage = pygame.transform.rotate(self.image, S.deg)
        self.width = blitimage.get_width()
        self.height = blitimage.get_height()
        blit = [self.flightcoord[0] - self.width//2,self.flightcoord[1] - self.height//2]

        #rect
        self.rect = pygame.Rect(self.flightcoord[0]- self.width//2 ,self.flightcoord[1] - self.height//2,self.width,self.height)

        #write
        window.blit(blitimage,(blit[0] , blit[1]))

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
        self.brek = pygame.mixer.Sound("sounds\\shield_break.wav")

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

        #gameplay
        self.health = 8

class Block(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\1x1.png")

        super().__init__(held)

        #gameplay
        self.sig = "block"
        self.deg = 1

class Corner(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\corner.png")

        super().__init__(held)

        #gameplay
        self.sig = "corner"
        self.cost = 25
        self.allow = [False, False, True, True]

class Concave(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\concave.png")

        super().__init__(held)

        #gameplay
        self.sig = "concave"
        self.cost = 25
        self.allow = [False, True, True, True]

class Convex(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\convex.png")

        super().__init__(held)

        #gameplay
        self.sig = "convex"
        self.cost = 25
        self.allow = [False, False, True, False]


class Gun(Part):
    def __init__(self, held):
        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\\gun.wav")]
        self.pew = pygame.mixer.Sound("sounds\\bit.wav")

        super().__init__(held)

        #gameplay
        self.sig = "gun"
        self.cost = 100
        self.allow = [False, False, True, False]

    def Fire(self):
        pygame.mixer.Sound.play(self.pew)
        deg = S.deg + self.deg + 180
        B.projectiles.append(Projectile(copy.deepcopy(self.flightcoord), copy.deepcopy(S.u), deg))

class Cannon(Gun):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\cannon.png")

        super().__init__(held)


class Particle:
    def __init__(self, coord, colour, vel, above):
        self.above = above
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
            if self.above:
                B.particlesabove.remove(self)
            else:
                B.particlesbelow.remove(self)

class Star:
    def __init__(self, coord):
        self.coord = [coord[0]+random.randint(-100,100), coord[1]+random.randint(-100,100)]
        
    def ArenaCheck(self):
        #arena check
        x = self.coord[0] - B.arenacoord[0]
        y = self.coord[1] - B.arenacoord[1]
        hypotenuse = math.sqrt(x**2 + y**2)

        #if hypotenuse < B.arenaradius:
        #    B.stars.remove(self)
        
    def Show(self):
        pygame.draw.circle(window, (214,245,246), (int(self.coord[0]), int(self.coord[1])), 3, 0)

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
        #reload
        if S.firedelay > 0:
            S.firedelay -= 1

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
            if S.firedelay == 0:
                for i in B.parts:
                    if i.sig == "gun":
                        i.Fire()
                S.firedelay = S.reload
        if keys[pygame.K_TAB]:
            S.jumpdelay = 50

    def FlightClickDOWN(self):
        #exit
        if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
            B.RUN = False

        #effects
        for i in range(0,25):
            B.particlesabove.append(Particle(self.coord, (214,245,246), 3, True))

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
            B.particlesabove.append(Particle(self.coord, (214,245,246), 3, True))

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

            #options
            elif self.highlight == -2:
                B.textboxtext = ""
                B.optionsinput = "save"
            elif self.highlight == -3:
                B.textboxtext = ""
                B.optionsinput = "load"

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
                    B.particlesabove.append(Particle(i.coord, (116,116,116), 5, True))

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
        if not B.optionsinput:
            M.BuildInput()
        else:
            B.Textbox()
    else:
        M.FlightInput()
        if S.jumpdelay > 0:
            S.Jump()
    
    #calc
    if not B.buildmode:
        S.Calculate()
        for i in B.projectiles:
            i.Calculate()
            i.Impact()

    #show
    B.Show()
    for i in B.particlesbelow:
        i.Show()
    if B.buildmode: 
        for i in B.parts:
            i.BuildShow()
    else:
        for i in B.projectiles:
            i.Show()
        for i in B.parts:
            i.FlightShow()
    for i in B.particlesabove:
        i.Show()

    #reset
    if not B.buildmode:
        S.Reset()
        for i in B.projectiles:
            i.Reset()
    
    pygame.display.update()
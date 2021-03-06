import pygame
from pygame import FULLSCREEN
import random
import time
import math
import copy
import os

#window setup
import ctypes
user32 = ctypes.windll.user32
global scr_width
global scr_height
scr_width = user32.GetSystemMetrics(0)
scr_height = user32.GetSystemMetrics(1)
window = pygame.display.set_mode((scr_width,scr_height),FULLSCREEN)
pygame.display.set_caption("SPRUCE")
pygame.font.init()
from pygame.locals import *
pygame.init()


#Objects
#BOARD ========================================
class Board:
    def __init__(self):
        #gameplay
        self.RUN = True
        self.garage = False
        self.ships = []
        self.parts = []
        self.stars = []
        self.particlesabove = []
        self.particlesbelow = []
        self.projectiles = []
        self.explosions = []
        self.broken = []
        self.credits = 1000
        self.score = 0

        #arena
        self.arenacoord = [scr_width//2, scr_height//2]
        self.arenaradius = 1500

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
                BoxFont = pygame.font.SysFont('', 25)
                Text = BoxFont.render(self.textboxtext, False, (247,216,148))
                window.blit(Text, (self.options[-1][0], self.options[-1][1] + self.options[-1][3]))

        else:
            #arena
            pygame.draw.circle(window, (214,245,246), (int(self.arenacoord[0]), int(self.arenacoord[1])), int(self.arenaradius), 10)
            for i in self.stars:
                i.Show()


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
        for i in S.parts:
            bind = False
            for x in ticker:
                for p in S.parts:
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
            S.parts.remove(M.selected)
        self.parts = []
            
        #connected check
        if not self.ConnectedScan():
            self.BuildmodeTransition()
        
        #empty check
        if len(S.parts) == 0:
            self.BuildmodeTransition()

        #ship
        S.Calibrate()

        #arena check
        self.GenArena()

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

    def GenArena(self):
        #arena
        self.stars = []
        ticker = [[-1,1],[1,-1],[-1,-1],[1,1]]
        for x in range(0,10):
            for y in range(0,10):
                for i in ticker:
                    X, Y = self.arenacoord[0]+i[0]*x*300, self.arenacoord[1]+i[1]*y*300
                    self.stars.append(Star([X, Y]))
        
        Remove = []
        for i in self.stars:
            if i.ArenaCheck():
                Remove.append(i)

        for i in Remove:
            self.stars.remove(i)

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
                S.Save(self.textboxtext)
            elif self.optionsinput == "load":
                S.Load(self.textboxtext, False)
            self.optionsinput = False

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
                    if B.garage != False:
                        if B.garage.dock:
                            for i in S.parts:
                                i.health == i.maxhealth
                                if i.sig == "shield":
                                    i.image = i.on
                            B.BuildmodeTransition()
                if not S.dead:
                    if keys[pygame.K_TAB]:
                        S.jumpdelay = 50
                    if keys[pygame.K_ESCAPE]:
                        PauseScreen()
        if not S.dead:
            if keys[pygame.K_w]:
                S.Active()
            if keys[pygame.K_a]:
                S.Turn(True)
            if keys[pygame.K_d]:
                S.Turn(False)
            if keys[pygame.K_SPACE]:
                if S.firedelay == 0:
                    for i in S.parts:
                        if i.sig == "cannon":
                            i.Fire()
                    S.firedelay = S.reload
        if keys[pygame.K_RETURN]:
            if S.dead:
                B.RUN = False

    def FlightClickDOWN(self):
        #exit
        if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
            B.RUN = False
            global RESPAWN
            RESPAWN = False

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
            global RESPAWN
            RESPAWN = False

        #effects
        for i in range(0,25):
            B.particlesabove.append(Particle(self.coord, (214,245,246), 3, True))

        #generate
        if self.found:
            for i in S.parts:
                if i.pycoord == self.pycoord and i.sig != "cockpit":
                    i.Lift()
                    self.selected = i
                    break 
        elif B.credits > 0:
            #left bar
            items = [Engine(True), Cannon(True), Shield(True), Gyro(True), Block(True), Corner(True), Concave(True), Convex(True)]
            if self.highlight >= 0:
                S.parts.append(items[self.highlight])
                self.selected = S.parts[-1]

            #credits + sound
            if self.selected != False:
                #credits
                B.credits -= self.selected.cost
                if B.credits < 0:
                    B.credits = 0
                
                #sound
                pygame.mixer.Sound.play(self.selected.liftsound)

        #options
        if self.highlight == -2:
            B.textboxtext = ""
            B.optionsinput = "save"
        elif self.highlight == -3:
            B.textboxtext = ""
            B.optionsinput = "load"
        
    def BuildClickUP(self):
        self.Coordfinder()

        if self.found:
            #occupied
            occupied = False
            for i in S.parts:
                if i.pycoord == self.pycoord:
                    occupied = True
                    break
            
            #verdict
            if occupied:
                B.credits += self.selected.cost
                S.parts.remove(self.selected)
            else:
                self.selected.Drop(copy.deepcopy(self.pycoord))
        else:
            B.credits += self.selected.cost
            S.parts.remove(self.selected)

        self.selected = False
                
    def Delete(self):
        self.Coordfinder()

        #scan
        for i in S.parts:
            if i.pycoord == self.pycoord and i.sig != "cockpit":
                #effects
                for p in range(0,50):
                    B.particlesabove.append(Particle(i.coord, (116,116,116), 5, True))

                B.credits += i.cost

                S.parts.remove(i)
                break

#ENTITIES ========================================
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

    def BoundaryCheck(self):
        x = self.coord[0] - B.arenacoord[0] 
        y = self.coord[1] - B.arenacoord[1] 
        self.hypotenuse = math.sqrt(x**2 + y**2)

        if self.hypotenuse > B.arenaradius:
            for i in range(0, 2):
                self.u[i] = -self.u[i]
                self.a[i] = -self.a[i]

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
            
class Projectile(Entity):
    def __init__(self, coord, u, deg, ship):
        #inheritance
        super().__init__()
        self.u = u
        self.deg = deg
        self.ship = ship

        #images
        self.coord = coord
        self.image = pygame.image.load("images\\projectile.png").convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(self.coord[0],self.coord[1],self.width,self.height)

        #gameplay
        self.m = 5
        self.Launch()
    
    def Launch(self):
        self.strength = 100

        #pythagoras
        radians = math.radians(self.deg)
        opp = self.strength * math.sin(radians)
        adj = self.strength * math.cos(radians)
        self.F[0] = -opp
        self.F[1] = adj

    def Show(self):
        #blit
        blitimage = pygame.transform.rotate(self.image, self.deg)
        self.width = blitimage.get_width()
        self.height = blitimage.get_height()
        blit = [self.coord[0] - self.width//2,self.coord[1] - self.height//2]

        #rect
        self.rect = pygame.Rect(self.coord[0],self.coord[1],self.width,self.height)

        #write
        window.blit(blitimage,(blit[0] , blit[1]))

    def BoundaryCheck(self):
        if math.sqrt(self.u[0]**2 + self.u[1]**2) < 0.01:
            self.Terminate()

        x = self.coord[0] - B.arenacoord[0] 
        y = self.coord[1] - B.arenacoord[1] 
        self.hypotenuse = math.sqrt(x**2 + y**2)

        if self.hypotenuse > B.arenaradius:
            self.Terminate()

    def Impact(self):
        dead = False
        for x in B.ships:
            if x != self.ship:
                for i in x.parts:
                    if self.rect.colliderect(i.rect):
                        if x.shield > 0:
                            x.shield -= 1
                            if x.shield % 5 == 0:
                                for y in x.parts:
                                    if y.sig == "shield" and y.image == y.on:
                                        y.Break()
                                        break

                        else:
                            i.health -= 1
                            if i.health <= 0:
                                i.Dead(x, False)
                        if len(x.parts) != 0:
                            for i in range(0,2):
                                #finds momentum      
                                self.p = self.m * self.u[i]
                                x_p = x.m * x.u[i]
                                #combines momentum
                                totalp = self.p + x_p
                                #finds u
                                x.u[i] = totalp / x.m

                        dead = True
                        break
                if dead:
                    break
        if dead:
            self.Terminate()
    
    def Terminate(self):
        try:
            B.projectiles.remove(self)
            B.explosions.append(Explosion(self.coord, 0))
        except:
            ValueError
                 
#SHIPS ========================================
class Ship(Entity):
    def __init__(self):
        #inheritance
        self.sig = "player"
        self.dead = False
        super().__init__()

        #sounds
        self.jump = pygame.mixer.Sound("sounds\\jump.wav") 

        #gameplay
        self.parts = []
        self.jumpdelay = 0
        self.firedelay = 0
        self.reload = 10

    def Calibrate(self):
        super().__init__()
        if self.sig == "NPC":
            self.deg = self.bypass

        #parts===
        for i in self.parts:
            #find CP
            if i.sig == "cockpit":
                CP = i
                self.coord = copy.deepcopy(i.coord)
        for i in self.parts:
            #hypotenuse
            x = i.coord[0] - CP.coord[0] #x is positive when part is to the right of CP
            y = i.coord[1] - CP.coord[1] #y is positive when part is below CP
            i.hypotenuse = math.sqrt(x**2 + y**2)

            #flightdeg
            i.flightdeg = self.deg
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

        #ship===                
        self.Accumulate()
        self.shield = self.maxshield

    def Accumulate(self):
        #accumulate values
        self.turnspeed = 0
        self.strength = 0
        self.m = 0
        self.maxshield = 0
        for i in self.parts:
            self.m += i.m #mass

            if i.sig == "gyro": #turn speed
                self.turnspeed += 0.5

            if i.sig == "engine": #thrust
                self.strength -= 10

            if i.sig == "shield": #shield
                self.maxshield += 5

    def Displace(self):
        if B.garage != False:
            B.garage.coord[0] += self.s[0]
            B.garage.coord[1] -= self.s[1]
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
        for x in B.ships:
            if x.sig == "NPC":
                x.coord[0] += self.s[0]
                x.coord[1] -= self.s[1]
                for i in x.parts:
                    i.flightcoord[0] += self.s[0]
                    i.flightcoord[1] -= self.s[1]
        for i in B.explosions:
            i.coord[0] += self.s[0]
            i.coord[1] -= self.s[1]
        for i in B.broken:
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
        for i in self.parts:
            if i.sig == "engine":
                i.image = i.off

    def Active(self):
        #show engines on
        for i in self.parts:
            if i.sig == "engine":
                i.image = i.on
                for x in range(0,3):
                    B.particlesbelow.append(Particle(i.flightcoord, (214,245,246), 10, False))
                    B.particlesbelow[-1].deg = self.deg + i.deg + random.randint(-50,50)

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
        if self.deg > 360:
            self.deg -= 360
        elif self.deg < 0:
            self.deg += 360

        for i in self.parts:
            if i.sig != "cockpit":
                i.flightdeg += change
                i.Displace(self)

    def Jump(self):
        for i in self.parts:
            for x in range(0, 3 -self.jumpdelay//15):
                deg = self.deg + random.randint(-50,50)
                radians = math.radians(deg)
                opp = 30 * math.sin(radians)
                adj = 30 * math.cos(radians)
                coord = [i.flightcoord[0]- opp, i.flightcoord[1]- adj] 
                B.particlesabove.append(Particle(coord, (255,255,255), 25 -self.jumpdelay//2, True))
                B.particlesabove[-1].deg = deg
        
        self.jumpdelay -= 1

        #arena check
        if self.jumpdelay == 0:
            B.broken = []
            pygame.mixer.Sound.play(self.jump)
            deg = self.deg + 180
            radians = math.radians(deg)
            opp = (B.arenaradius - 300) * math.sin(radians)
            adj = (B.arenaradius - 300) * math.cos(radians)

            B.arenacoord = [scr_width//2, scr_height//2]
            B.arenacoord = [B.arenacoord[0]+opp, B.arenacoord[1]+adj]
            B.GenArena()

            #score
            score = B.credits
            for i in S.parts:
                score += i.cost
            if score > B.score:
                B.score = score
            

            #enemy + garage
            for i in B.ships:
                if i.sig == "NPC":
                    for x in i.parts:
                        if x.sig == "cockpit":
                            x.Dead(i, True)

            if random.randint(0,4) == 0:
                B.garage = Garage()
            else:
                B.garage = False
                B.ships.append(Enemy(deg + random.randint(-80,80)))

    def Load(self, name, big):
        #resets parts
        Remove = []
        for i in self.parts:
            if i.sig == "cockpit":
                i.Drop([B.width//2, B.height//2])
            else:
                Remove.append(i)
            B.credits += i.cost

        for i in Remove:
            self.parts.remove(i)

        try:
            f = open(("big"*big)+"ships\\"+name+".txt", "r")

            #cycles the data
            signatures = ["engine", "cannon", "shield", "gyro", "block", "corner", "concave", "convex"]

            for line in f:
                items = [Engine(False), Cannon(False), Shield(False), Gyro(False), Block(False), Corner(False), Concave(False), Convex(False)]
                chunks = line.split(",")
                if len(chunks) == 1 and self.sig == "player":
                    B.credits -= int(chunks[0])
                else:
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
        f = open("ships\\"+name+".txt", "w")
        
        total = 0
        for i in self.parts:
            if i.sig != "cockpit":
                f.write(i.sig+","+str(i.pycoord[0])+","+str(i.pycoord[1])+","+str(i.deg)+"\n")
            total += i.cost
        
        f.write(str(total))
        f.close()

class Enemy(Ship):
    def __init__(self, deg):
        #inheritance
        super().__init__()
        self.sig = "NPC"
        self.bypass = deg
        radians = math.radians(deg)
        self.opp = (B.arenaradius - 300) * math.sin(radians)
        self.adj = (B.arenaradius - 300) * math.cos(radians)
        self.verdict = [False, False, False]

        #cockpit
        self.parts.append(Cockpit(False))
        self.parts[-1].Drop([scr_width//2, scr_height//2])
        
        #find blueprint
        score = B.credits
        for i in S.parts:
            score += i.cost
        if score > 2500:
            blue = random.choice(os.listdir("bigships\\"))
            big = True
        else:
            blue = random.choice(os.listdir("ships\\"))
            big = False
        blue = blue[:-4]
        self.Load(blue, big)

        #calibrates parts
        self.Calibrate()
        self.coord = [B.arenacoord[0]+self.opp, B.arenacoord[1]+self.adj]
        for i in self.parts:
            i.Displace(self)

    def Ai(self):
        if self.firedelay > 0:
            self.firedelay -= 1
        fired = False
        for i in self.parts:
            if i.sig == "cannon":
                result = i.FindSight(self)
                i.sight = pygame.draw.line(window,(255,0,0), (i.flightcoord), (result))


                for x in S.parts:
                    if i.sight.colliderect(x.rect):
                        if self.firedelay == 0:
                            i.Fire()
                            fired = True
                            break
                        
        if fired:
            self.firedelay = self.reload

        self.Movement()
        if self.verdict[0]:
            self.Active()
            
        if self.verdict[1]:
            self.Turn(True)
        elif self.verdict[2]:
            self.Turn(False)
        
    def Movement(self):
        #forward
        Forward = False
        x = S.coord[0] - self.coord[0] 
        y = S.coord[1] - self.coord[1] 
        hypotenuse = math.sqrt(x**2 + y**2)

        if hypotenuse > 300:
            Forward = True

        #turn
        Turn = [False, False]
        trig = math.degrees(math.asin(x/hypotenuse))
        orient = round(trig)
        deg = 180

        if y > 0:
            deg += trig
        else:
            if orient > 0:
                deg += 90 - trig
            elif orient < 0:
                deg += -90 - trig
        if y < 0: 
            if orient > 0:
                deg += 90
            elif orient < 0:
                deg -= 90
            else:
                deg = 180

        rad = math.radians(self.deg - deg)
        opp = math.sin(rad)
        if opp < 0:
            Turn[0] = True
        elif opp > 0:
            Turn[1] = True

        self.verdict = [Forward, Turn[0], Turn[1]]

    def Displace(self):
        self.coord[0] -= self.s[0]
        self.coord[1] += self.s[1]
        for i in self.parts:
            i.flightcoord[0] -= self.s[0]
            i.flightcoord[1] += self.s[1]

class Garage:
    def __init__(self):
        #image
        self.on = pygame.image.load("images\\garage_on.png").convert_alpha()
        self.off = pygame.image.load("images\\garage_off.png").convert_alpha()
        self.image = self.on
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        #gameplay
        self.dock = False
        coord = copy.deepcopy(B.arenacoord)
        self.coord = [coord[0]-self.width //2, coord[1]- self.height//2]

    def Show(self):
        x = (self.coord[0] < S.coord[0] < self.coord[0] + self.width)
        y = (self.coord[1] < S.coord[1] < self.coord[1] + self.height)

        if x and y:
            image = self.on
            self.dock = True
        else:
            image = self.off
            self.dock = False
        window.blit(image,(self.coord[0] , self.coord[1]))


#PARTS ========================================
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
        self.m = 50
        self.maxhealth = 3
        self.health = self.maxhealth
        self.allow = [True, True, True, True] #starts top, cycles clockwise
        
        #image
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

    def FlightShow(self, ship):
        #blit
        blitimage = pygame.transform.rotate(self.image, ship.deg)
        self.width = blitimage.get_width()
        self.height = blitimage.get_height()
        blit = [self.flightcoord[0] - self.width//2,self.flightcoord[1] - self.height//2]

        #rect
        self.rect = pygame.Rect(self.flightcoord[0]- self.width//2 ,self.flightcoord[1] - self.height//2,self.width,self.height)

        #write
        window.blit(blitimage,(blit[0] , blit[1]))

    def Displace(self, ship):
        rad = math.radians(self.flightdeg)
        y = ship.coord[1] + self.hypotenuse*math.cos(rad)
        x = ship.coord[0] + self.hypotenuse*math.sin(rad)

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

    def Dead(self, ship, jump):
        #remove part
        if ship != False:
            ship.parts.remove(self)
            if len(ship.parts) == 0 or self.sig == "cockpit":
                for i in ship.parts:
                    i.Dead(False, jump)
                
                if ship.sig == "player":
                    ship.dead = True
                else:
                    B.ships.remove(ship)
            ship.Accumulate()

        if not jump:
            if ship != S:
                B.credits += self.cost//4
            coord = [self.flightcoord[0] + self.width//2,self.flightcoord[1] + self.height//2]
            B.explosions.append(Explosion(coord, 1))
            B.broken.append(Broken(self.flightcoord, self.sig, self.m))

class Cockpit(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\cockpit.png").convert_alpha()

        #sound
        self.dropsound = [pygame.mixer.Sound("sounds\\cockpit.wav")]

        super().__init__(held)
        
        #gameplay
        
        self.sig = "cockpit"

class Engine(Part):
    def __init__(self, held):
        #image
        self.on = pygame.image.load("images\\engine_on.png").convert_alpha()
        self.off = pygame.image.load("images\\engine_off.png").convert_alpha()
        self.image = self.off

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
        self.on = pygame.image.load("images\\shield_on.png").convert_alpha()
        self.off = pygame.image.load("images\\shield_off.png").convert_alpha()
        self.image = self.on

        #sounds
        self.dropsound = [pygame.mixer.Sound("sounds\\shield_regen.wav")]
        self.brek = pygame.mixer.Sound("sounds\\shield_break.wav")

        super().__init__(held)

        #gameplay
        self.cost = 200
        self.m = 50
        self.sig = "shield"
        self.deg = 1

    def Break(self):
        pygame.mixer.Sound.play(self.brek)
        self.image = self.off

class Gyro(Part):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\gyro.png").convert_alpha()

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
        self.maxhealth = 8
        self.health = self.maxhealth

class Block(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\1x1.png").convert_alpha()

        super().__init__(held)

        #gameplay
        self.sig = "block"
        self.deg = 1

class Corner(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\corner.png").convert_alpha()

        super().__init__(held)

        #gameplay
        self.sig = "corner"
        self.cost = 25
        self.allow = [False, False, True, True]

class Concave(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\concave.png").convert_alpha()

        super().__init__(held)

        #gameplay
        self.sig = "concave"
        self.cost = 25
        self.allow = [False, True, True, True]

class Convex(Hull):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\convex.png").convert_alpha()

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
        self.cost = 100
        self.allow = [False, False, True, False]

    def Fire(self):
        ship = 0
        for x in B.ships:
            for i in x.parts:
                if i == self:
                    ship = x
                    break

        pygame.mixer.Sound.play(self.pew)
        deg = ship.deg + self.deg + 180
        B.projectiles.append(Projectile(copy.deepcopy(self.flightcoord), copy.deepcopy(ship.u), deg, ship))

    def FindSight(self, ship):
        #hypotenuse
        hypotenuse = 1000
        #calc
        rad = math.radians(ship.deg + self.deg + 180)
        coord = self.flightcoord

        x = hypotenuse* math.sin(rad)
        y = hypotenuse* math.cos(rad)

        result = [coord[0]+x, coord[1]+y]
        return result

class Cannon(Gun):
    def __init__(self, held):
        #image
        self.image = pygame.image.load("images\\cannon.png").convert_alpha()

        super().__init__(held)

        #gameplay
        self.sig = "cannon"


#EFFECTS ========================================
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

        if hypotenuse > B.arenaradius:
            return True
        else:
            return False
        
    def Show(self):
        pygame.draw.circle(window, (214,245,246), (int(self.coord[0]), int(self.coord[1])), 3, 0)

class Explosion:
    def __init__(self, coord, big):
        #images
        self.cycle = []
        for i in range(1,7):
            self.cycle.append(pygame.image.load("images\\explosions\\"+(big*"big")+"explosion#"+str(i)+".png").convert_alpha())
        #behaviour
        self.index = 0
        self.image = self.cycle[self.index]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.coord = [coord[0]-self.width/2, coord[1]-self.height/2]
        self.delay = 5

        
        if big:
            #sound
            self.explod = pygame.mixer.Sound("sounds\\explod.wav")
            pygame.mixer.Sound.play(self.explod)

            #particle effects
            for p in range(0,50):
                B.particlesabove.append(Particle(self.coord, (51,66,77), 10, True))

    def Show(self):
        #show
        self.image = self.cycle[self.index]
        window.blit(self.image, (self.coord[0],self.coord[1]))

        #time
        if self.delay < 0:
            self.index += 1
            self.delay = 5
        else:
            self.delay -= 1

        #terminate
        if self.index > 5:
            B.explosions.remove(self)

class Broken(Entity):
    def __init__(self, coord, image, m):
        #inheritance
        super().__init__()
        self.F = [random.randint(-50,50),random.randint(-50,50)]
        self.m = m

        #image
        self.image = pygame.image.load("images\\dead\\"+image+".png").convert_alpha()     

        #details
        self.coord = coord
        self.width = self.image.get_width
        self.height = self.image.get_height
        self.deg = random.randint(0,360)

    def Show(self):
        #blit
        blitimage = pygame.transform.rotate(self.image, self.deg)
        self.width = blitimage.get_width()
        self.height = blitimage.get_height()
        blit = [self.coord[0] - self.width//2,self.coord[1] - self.height//2]

        #write
        window.blit(blitimage,(blit[0] , blit[1]))

#menus
def TitleScreen():
    TitleFont = pygame.font.SysFont('', 550)
    SubFont = pygame.font.SysFont('', 20)
    loop = True
    while loop:
        window.fill((33,44,48))
        
        #title
        Text = TitleFont.render('SPRUCE', False, (201,115,81))
        window.blit(Text,(scr_width/2-750,scr_height/2-200))

        #subtitle
        Login = SubFont.render('PRESS ENTER TO START', False, (255,255,255))
        window.blit(Login,(scr_width/2-90,scr_height/2+110))
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_RETURN]:
                        loop = False
                        
        pygame.display.update()

def PauseScreen():
    TitleFont = pygame.font.SysFont('', 550)
    SubFont = pygame.font.SysFont('', 20)
    loop = True
    while loop:
        window.fill((33,44,48))
        
        #title
        Text = TitleFont.render('PAUSED', False, (201,115,81))
        window.blit(Text,(scr_width/2-750,scr_height/2-200))
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    loop = False
                        
        pygame.display.update()

def ScoreBox():
    #worth 
    pygame.draw.rect(window, (40,62,63), (scr_width//2-200, scr_height//2-100, 400,200))

    #subtitle
    SubFont = pygame.font.SysFont('', 50)
    Text = SubFont.render("SCORE", False, (247,216,148))
    window.blit(Text, (scr_width//2-200, scr_height//2-90))
    
    #retry
    SubFont = pygame.font.SysFont('', 20)
    Text = SubFont.render('PRESS ENTER TO RETRY', False, (255,255,255))
    window.blit(Text,(scr_width/2-90,scr_height/2+110))

    #score
    ScoreFont = pygame.font.SysFont('', 200)
    Text = ScoreFont.render(str(B.score), False, (201,115,81))
    window.blit(Text, (scr_width//2-180, scr_height//2-50))

if __name__ == '__main__':
    global RESPAWN
    RESPAWN = True
    while RESPAWN:
        M = Mouse()
        B = Board()
        S = Ship()
        B.ships.append(S)
        B.garage = Garage()
        #cockpit
        S.parts.append(Cockpit(False))
        S.parts[-1].Drop([B.width//2, B.height//2])

        TitleScreen()
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
                if S.jumpdelay > 0:
                    S.Jump()
                else:
                    M.FlightInput()
                for x in B.ships:
                    if x.sig != "player":
                        x.Ai()
            
            #calc
                for x in B.ships:
                    x.Calculate()
                for i in B.projectiles:
                    i.Calculate()
                    i.Impact()
                for i in B.broken:
                    i.Calculate()

            #show
            B.Show()
            
            for i in B.particlesbelow:
                i.Show()
            if B.buildmode: 
                for i in S.parts:
                    i.BuildShow()
                for i in B.items:
                    i.BuildShow()
            else:
                if B.garage != False:
                    B.garage.Show()
                for i in B.broken:
                    i.Show()
                for i in B.projectiles:
                    i.Show()
                for x in B.ships:
                    for i in x.parts:
                        i.FlightShow(x)
                for i in B.explosions:
                    i.Show()
                if S.dead:
                    ScoreBox()
                
            for i in B.particlesabove:
                i.Show()

            #reset
            if not B.buildmode:
                for x in B.ships:
                    x.Reset()
                for i in B.projectiles:
                    i.Reset()
                for i in B.broken:
                    i.Reset()
            
            pygame.display.update()
#####################################################################
#
#
#   Blasterama.py
#
#   7th October 2008
#   rsbrooks@gmail.com
#
#   A no holes barred shootem up.  No rules, just shot as
#   many aliens as you can in wave after wave.  You have as
#   many lives / shields as you want.  Watch out for the initial
#   wave swarm, it's a killer !
#
#   left and right arrow to steer the ship, z key to fire.
#
#
#
#####################################################################

import pygame, math, random
from pygame.locals import *
import sys
import os

#######################
#### Sprite subclasses
#######################
class StatusDisplay(pygame.sprite.Sprite):
    """ this class is used to display the score etc at the top of the screen"""
    def __init__(self, G):
        pygame.sprite.Sprite.__init__(self)
        self.G = G
        self.lives = 0
        self.score = 0
        self.wave = 1
        self.font = pygame.font.Font("hhead.ttf", 32)
        self.layer = None # pygame.Surface((G['screen'].get_rect().width, self.bg.get_rect().height))
        self.image = None # self.layer
        self.rect = None # self.image.get_rect()

    def update(self,lives,score):
        lives_bg = self.font.render("lives: %d" % lives, 1, (255, 255, 255))
        lives_fg = self.font.render("lives: %d" % lives, 1, (0, 64, 224))
        score_bg = self.font.render("score: %05d" % score, 1, (255, 255, 255))
        score_fg = self.font.render("score: %05d" % score, 1, (0, 64, 224))

        title_bg = self.font.render("B L A S T E R A M A", 1, (255,255,255))
        title_fg = self.font.render("B L A S T E R A M A", 1, (224,0,64))

        lives_bg.blit(lives_fg, (1,1))
        score_bg.blit(score_fg, (1,1))
        title_bg.blit(title_fg,(1,1))
        
        if self.layer == None : 
            self.layer = pygame.Surface((self.G['screen'].get_rect().width,lives_bg.get_rect().height))

        self.layer.fill((128,128,128))    

        # Left align
        self.layer.blit(score_bg,(5,0))

        # Center align
        sbar = self.layer.get_rect()
        self.layer.blit(title_bg,((sbar.width/2)-title_bg.get_rect().width/2,0))
        
        # Right align
        self.layer.blit(lives_bg,(sbar.width-lives_bg.get_rect().width-5,0))
        
        self.image = self.layer
        self.rect = self.image.get_rect()
        
class Background (pygame.sprite.Sprite) :
    """ for scrolling background """
    def __init__(self,G, path) :
        pygame.spite.Sprite.__init__(self)
        self.G = G
        self.path = path
        if os.path.exists(path) :
            self.image = pygame.image.load(G['bg_image']).convert()
            self.rect = self.image.get_rect()
        
    def update(self) :
        self.rect.topleft = (0,0)
        
class Alien (pygame.sprite.Sprite):
    """  Alien class - inherits from pygame Sprite class - all the aliens on the screen"""
    def __init__(self, G):
        pygame.sprite.Sprite.__init__(self)
        self.G = G
        self.imagearray=[]
        self.images = pygame.image.load('light.bmp').convert()
        self.images.set_colorkey((255,0,255))
        scaling = [1, 1.2, 1.5, 2]
        self.scale = scaling[random.randrange(0,len(scaling))]
        for i in range(0,120,24):
            frame = self.images.subsurface((i,0,24,24))
            r = frame.get_rect()
            frame = pygame.transform.scale(frame, (r.width*self.scale,r.height*self.scale))  
            self.imagearray.append(frame)
        self.image = self.imagearray[0]
        self.rect = self.imagearray[0].get_rect()
        
        # Initial placement based on screen size
        src = self.G['screen'].get_rect()
        sbar = self.G['status'].layer.get_rect()
        self.rect.topleft = [random.randrange(0,src.width-self.rect.width), \
                             random.randrange(sbar.height+1,src.height/3)]

        # Actually, this is x,y speed
        self.direction = [random.randrange(1,5),random.randrange(1,5)]
        self.movement_ticks = 0
        self.animationcounter = random.randrange(0,4)
        self.animation_ticks = 0

    # Create max_aliens worth of sprites for the given RenderUpdates object
    @classmethod
    def create_horde(cls,RU,G,num) :
        i = 0
        while i < num :
            RU.add(Alien(G))
            i += 1

    def update(self,timer):
        if self.movement_ticks < timer:
            self.movment_ticks = timer
            scr = self.G['screen'].get_rect()
            sbar = self.G['status'].layer.get_rect()
            if self.rect.left < 0 \
                  or self.rect.left > (scr.width-self.rect.width) :
                self.direction[0] = -self.direction[0]
                
            if self.rect.top < sbar.height \
                   or self.rect.top > (scr.height - self.rect.height):
                self.direction[1] = -self.direction[1]

            self.rect.left = self.rect.left + self.direction[0]
            self.rect.top = self.rect.top + self.direction[1]

            self.movement_ticks += 20

            self.image = self.imagearray[self.animationcounter]
            if self.animation_ticks < timer:
                self.animation_ticks = timer
                self.animationcounter -= 1
                if self.animationcounter < 0:
                    self.animationcounter = 4
                self.animation_ticks += 150

class BaseShip(pygame.sprite.Sprite):
    """ the BaseShip class """
    D_LEFT = 100
    D_RIGHT = 200

    def __init__(self, G):
        pygame.sprite.Sprite.__init__(self)
        self.G = G
        self.speed = 4
        self.image = pygame.image.load('baseship.bmp').convert()
        self.image.set_colorkey((255,0,255))
        self.rect = self.image.get_rect()
        self.reset()
    
    def reset(self) : 
        self.lives = 3
        self.score = 0
        #[380,580]
        src = self.G['screen'].get_rect()
        self.rect.topleft = [((src.width/2)-self.rect.width), src.height-self.rect.height]

    def update(self):
        if self.G['ship_direction'] == self.D_LEFT and self.rect.left > 0 :
            self.rect.left -= self.speed
        elif self.G['ship_direction'] == self.D_RIGHT and self.rect.left < (self.G['screen'].get_rect().width-self.rect.width) :
            self.rect.left += self.speed

class Missile(pygame.sprite.Sprite):
    """ the Missile class """
    def __init__(self, initialposition):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('missile.bmp').convert()
        self.image.set_colorkey((255,0,255))
        self.rect = self.image.get_rect()
        self.rect.topleft = initialposition
        self.speed = 8

    def update(self):
        if self.rect.top > 0:
            self.rect.top -= self.speed
        else:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """  Explosion class - the explosions on screen obviously """
    def __init__(self, initialposition):
        pygame.sprite.Sprite.__init__(self)
        self.imagearray=[]
        self.images = pygame.image.load('explosion.bmp').convert()
        self.images.set_colorkey((255,0,255))
        for i in range(0,240,60):
            self.imagearray.append(self.images.subsurface((i,0,60,60)))
        self.image = self.imagearray[0]
        self.rect = self.imagearray[0].get_rect()
        self.animation_ticks = 0
        self.animationcounter = 0
        self.rect.topleft = initialposition

    def update(self,timer):
        if self.animation_ticks < timer:
            self.animation_ticks = timer
            self.image = self.imagearray[self.animationcounter]
            self.animationcounter += 1
            if self.animationcounter > 3: self.kill()
            self.animation_ticks += 50

def initSounds(G) : 

    pygame.mixer.pre_init(44000, 16, 2, 4096)
    G['s_missile'] = pygame.mixer.Sound('missile.wav')
    G['s_explosion'] = pygame.mixer.Sound('explosion.wav')
    G['s_basehit'] = pygame.mixer.Sound('basehit.wav')
    G['s_swarm'] = pygame.mixer.Sound('swarm.wav')

    G['s_missile'].set_volume(G['sfx_volume'])
    G['s_explosion'].set_volume(G['sfx_volume'])
    G['s_basehit'].set_volume(G['sfx_volume'])
    G['s_swarm'].set_volume(G['sfx_volume'])

    # BG music
    G['s_bg_music'] = "strauss_blue_danube.mid"
    if os.path.exists(G['s_bg_music']) :
        pygame.mixer.music.load(G['s_bg_music'])
        pygame.mixer.music.set_volume(G['bg_volume'])

def initGame() :
    WINSIZE = [800,600]
    G = {}
    G['screen'] = pygame.display.set_mode(WINSIZE)
    G['clock'] = pygame.time.Clock()
    G['time'] = pygame.time.get_ticks()
    G['missileticks']  = G['time']
    G['running'] = 1
    G['gameover'] = 0

    G['sfx_volume'] = 0.24
    G['bg_volume']  = 1
    
    G['ship_fired'] = 0 
    G['ship_direction'] = 3

#    # BG image
#    G['bg_image'] = "background3.bmp"
#    if os.path.exists(G['bg_image']) :
#            G['background'] = pygame.image.load(G['bg_image']).convert()
#            G['screen'].blit(G['background'],(0,0))
#            pygame.display.update()
            
    # Hide mouse
    pygame.mouse.set_visible(0)

    # Initialize joystick
    J=None
    DEBUG_JOYSTICK = False
    if not pygame.joystick.get_init() :
        if DEBUG_JOYSTICK :
            print "Joystick not enabled"
    else :
        if DEBUG_JOYSTICK :
            print "Found %d joysticks" % pygame.joystick.get_count()
        if (pygame.joystick.get_count() > 0) :
            J=pygame.joystick.Joystick(0)

    if J <> None :
        if not J.get_init() :
            J.init()
        if DEBUG_JOYSTICK :
            print "Using Joystick: %s" % J.get_name()
            print "  Number of axes:         %d" % J.get_numaxes()
            print "  Number of trackballs:   %d" % J.get_numballs()
            print "  Number of buttons:      %d" % J.get_numbuttons()
            print "  Number of hat controls: %d" % J.get_numhats()

    G['joystick'] = J
    initSounds(G)
    return G

def clearScreen(G) :
    #G['screen'].fill((0,0,0))
    G['screen'].blit(G['background'],(0,0))
    pygame.display.flip()

def displayMsg(S, msg) :
    # Create a drop-shadow
    F = pygame.font.Font("hhead.ttf", 48)
    s_bg = F.render(msg, 1, (255, 255, 255))
    s_fg = F.render(msg,1,(255,0,0))
    s_bg.blit(s_fg,(2,2))
    r = s_bg.get_rect()
    SR = S.get_rect()
    S.blit(s_bg, (SR.width/2-(r.width/2),SR.height/2))
    pygame.display.update()
    return s_bg
    
def makeSwarm(G) : 
    G['aliens'] = pygame.sprite.RenderUpdates()
    max = G['status'].wave * 15
    if max > 50 :
        max = 50
    Alien.create_horde(G['aliens'], G, max)
    G['s_swarm'].play()

def initSprites(G) :
    clearScreen(G)
    
    G['ru_background'] = pygame.sprite.RenderUpdates()
    B = Background(G,"background3.bmp")
    G['ru_background'].add(B)
    G['background'] = B.image

    G['ru_status'] = pygame.sprite.RenderUpdates()
    G['ru_status'].add(StatusDisplay(G))

    G['status'] = G['ru_status'].sprites()[0]
    G['ru_ship'] = pygame.sprite.RenderUpdates()
    G['ru_ship'].add(BaseShip(G))
    G['ship'] = G['ru_ship'].sprites()[0]
    G['ship'].reset()

    G['ru_missile'] = pygame.sprite.RenderUpdates()
    G['ru_explosion'] = pygame.sprite.RenderUpdates()
    
    G['ru_status'].update(G['ship'].lives,G['ship'].score)

    
def restartGame (G) :
    pygame.mixer.music.stop()
    initSprites(G)
    makeSwarm(G)

    G['surface_last_message'] = displayMsg(G['screen'], "Wave %d" % G['status'].wave)
    pygame.time.wait(2000)
    clearScreen(G)
    pygame.mixer.music.play(-1) # loop forever
    G['running']=1
    G['gameover']=0

def handleInput (G) :
    for e in pygame.event.get():
        if e.type == QUIT :
            sys.exit()
            
        if e.type == pygame.KEYDOWN :
            if e.key == pygame.K_ESCAPE or e.key == pygame.K_q :
                sys.exit()
            elif e.key == pygame.K_p :
                if G['running'] == 1 :
                    G['running'] = 0
                    pygame.mixer.music.pause()
                    
                else :
                    G['running'] = 1
                    pygame.mixer.music.unpause()

            elif e.key == pygame.K_n :
                # New game
                if G['gameover'] == 1 :
                    restartGame(G)

    # Avoid the event system for ship movement
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_LEFT] : 
        G['ship_direction'] = BaseShip.D_LEFT
    elif pressed_keys[K_RIGHT] : 
        G['ship_direction'] = BaseShip.D_RIGHT
    else :
        G['ship_direction'] = 0

    if pressed_keys[K_z] or pressed_keys[K_SPACE] : 
        G['ship_fired'] = 1
    else : 
        G['ship_fired'] = 0

    if G['joystick'] <> None :
        v1 = G['joystick'].get_axis(0)
        v2 = G['joystick'].get_axis(1)
        if v1 > 0.5  : 
            # Move left
            G['ship_direction'] = BaseShip.D_RIGHT
        elif v1 < -0.5 :
            # Move right
            G['ship_direction'] = BaseShip.D_LEFT

        if G['joystick'].get_button(0) :
            G['ship_fired'] = 1

        if G['joystick'].get_button(1) :
            if G['gameover'] : 
                restartGame(G)

def main():
    pygame.init()
    G = initGame()
    restartGame(G)

    while True :
        G['time'] = pygame.time.get_ticks()
        handleInput(G)

        # Game logic updates
        if G['running'] == 1 :
            if 'surface_last_message' in G :
                clearScreen(G)
                del G['surface_last_message']
            
            if G['ship_fired'] == 1 and G['time'] > G['missileticks']:
                G['missileticks'] = G['time'] + 300
                a,b,c,d = rectlistbaseship[0]
                G['ru_missile'].add(Missile((a+18,b)))
                G['s_missile'].play()

            G['screen'].blit(G['background'], (0,0))

            G['ru_ship'].clear(G['screen'],G['background'])
            G['aliens'].clear(G['screen'],G['background'])
            G['ru_missile'].clear(G['screen'],G['background'])
            G['ru_explosion'].clear(G['screen'],G['background'])
            G['ru_status'].clear(G['screen'],G['background'])

            G['ru_ship'].update()
            G['ru_missile'].update()
            G['aliens'].update(G['time'])
            G['ru_explosion'].update(G['time'])

            for i in pygame.sprite.groupcollide(G['aliens'], G['ru_missile'], True, True):
                a,b,c,d = i.rect
                G['ru_explosion'].add(Explosion((a-20,b-20)))
                G['ship'].score += 10
                G['ru_status'].update(G['ship'].lives,G['ship'].score)
                G['s_explosion'].play()

            for i in pygame.sprite.groupcollide(G['ru_ship'], G['aliens'], False, True):
                # Ship was hit
                a,b,c,d = i.rect
                # Is the shield on?
                G['ru_explosion'].add(Explosion((a-20,b-20)))
                G['ship'].lives -= 1
                G['s_basehit'].play()
                G['ru_status'].update(G['ship'].lives,G['ship'].score)

                if (G['ship'].lives < 1) :
                    G['gameover'] = 1
                    G['running'] = 0
                    pygame.mixer.music.stop()

                else :
                    displayMsg(G['screen'],"Ouch!")
                    pygame.time.wait(1000)
                    clearScreen(G)

            rectlistbaseship = G['ru_ship'].draw(G['screen'])
            rectlistmissiles = G['ru_missile'].draw(G['screen'])
            rectlistaliens = G['aliens'].draw(G['screen'])

            if len(rectlistaliens) == 0:
                pygame.mixer.music.stop()
                G['status'].wave += 1
                G['ship'].lives += 1
                G['surface_last_message']=displayMsg(G['screen'], "Wave %d" % G['status'].wave)
                pygame.time.wait(2000)
                clearScreen(G)
                makeSwarm(G)
                G['ru_status'].update(G['ship'].lives,G['ship'].score)
                pygame.mixer.music.play(-1) # loop forever

            rectlistexplosions = G['ru_explosion'].draw(G['screen'])
            rectliststatusdisplay = G['ru_status'].draw(G['screen'])

            pygame.display.update(rectlistbaseship)
            pygame.display.update(rectlistmissiles)
            pygame.display.update(rectlistaliens)
            pygame.display.update(rectlistexplosions)
            pygame.display.update(rectliststatusdisplay)
            pygame.display.update(G['sp_background'])

        else : 
            text = "P A U S E"
            if G['gameover'] == 1 :
                text = "G A M E O V E R"
                
            G['surface_last_message'] = displayMsg(G['screen'], text)
                        
        G['clock'].tick(60)

if __name__ == '__main__': main()

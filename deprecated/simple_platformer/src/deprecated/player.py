
import pygame

from simple_platformer.utilities import Vector2D, ScreenBounds
from simple_platformer.utilities import Colors, ScreenProperties


class Player(pygame.sprite.Sprite):
    
    # movement constants (screen origin is at the top left [0,0]) thus y values are inverted
    FALL_SPEED_INCREMENT = -0.35
    FALL_SPEED = -1
    JUMP_SPEED = 10
    JUMP_HIGHER_SPEED = 12
    PLATFORM_CHECK_STEP = 2
    X_STEP = 5
    
    def __init__(self):
        
        # superclass constructor
        pygame.sprite.Sprite.__init__(self)
        
        # Player speed
        self.incr = Vector2D(0,0) # increment in world coordinates
        #self.world_pos = Vector2D() # position of the top left of rectangle
        
        # Current level
        self.level = None
        
        # screen attributes
        self.screen_bounds = None
        
        # Graphics
        self.image = None
        self.rect = None
        
        # create player block
        self.image = pygame.Surface([40,60])
        self.image.fill(Colors.RED)
        self.rect = self.image.get_rect()
        self = pygame.sprite.Sprite()
        self.rect = self.rect.copy()
        
        print "Image size %i x %i at position [ %i , % i]"%(self.rect.width, self.rect.height,
                                                            self.rect.x,self.rect.y)
        
        print "Image bottom %i and top %i" %(self.rect.bottom,self.rect.top)
        
    def update(self):
        
        self.apply_vertical_motion()
        
        #self.world_pos.x += self.incr.x
        #self.world_pos.y += self.incr.y  
           
        
        # collisions and boundary checks
        self.check_collisions()
        self.check_level_bounds()
        self.check_screen_bounds()
        
        self.rect.x = self.rect.x
        self.rect.y = self.rect.y
        
    def apply_vertical_motion(self):
        
        if self.incr.y ==0: # on surface or end of jump
            self.incr.y = Player.FALL_SPEED
        else:
            self.incr.y += Player.FALL_SPEED_INCREMENT # increase fall speed        
            
                    
    def check_collisions(self):        
     
        
        # find colliding platforms in the y direction        
        self.rect.y -= self.incr.y # increment in screen coordinates   
        platforms = pygame.sprite.spritecollide(self,self.level.platforms,False)     
        for platform in platforms:
            
            # check for vertical overlaps
            if self.incr.y < 0: # falling
                self.rect.bottom = platform.rect.top
                self.incr.y = 0                
            elif self.incr.y > 0 : # ascending
                self.rect.top = platform.rect.bottom                
                self.incr.y = 0
                
        # find colliding platforms in the x direction            
        self.rect.x += self.incr.x # increment in screen coordinates 
        platforms = pygame.sprite.spritecollide(self,self.level.platforms,False)     
        for platform in platforms:
                
            # check for horizontal overlaps
            if self.incr.x < 0:
                self.rect.left = platform.rect.right
                #self.incr.x = 0
            elif self.incr.x > 0:                
                self.rect.right = platform.rect.left                
                #self.incr.x = 0                
                print "Collision to the right, shifted %d units"%(self.rect.right)            
            
        # endfor       
        
    def check_level_bounds(self):
        
        # vertical bounds
        if self.rect.bottom > self.level.rect.bottom : # below ground level
            self.rect.bottom = self.level.rect.bottom
            self.incr.y = 0
        elif self.rect.top < self.level.rect.top: # above level top
            self.rect.top = self.level.rect.top  
            self.incr.y = 0  
        
         
        # horizontal bounds
        if self.rect.right  > self.level.rect.right:
            self.rect.right  = self.level.rect.rigth
            self.incr.x = 0
            
        if self.rect.left < self.level.rect.left:
            self.rect.left = self.level.rect.left;
            self.incr.x = 0   
            
    def check_screen_bounds(self):
        
        scroll = Vector2D() # increment of level in world coordinates
        
        # vertical bounds
        if self.rect.bottom > self.screen_bounds.rect.bottom : # below ground level
            scroll.y = -(self.screen_bounds.rect.bottom - self.rect.bottom)
            self.rect.bottom = self.screen_bounds.rect.bottom
            
        elif self.rect.top < self.screen_bounds.rect.top: # above level top
            scroll.y = -(self.screen_bounds.rect.top - self.rect.top)
            self.rect.top = self.screen_bounds.rect.top 
            
        # horizontal bounds
        if self.rect.right > self.screen_bounds.rect.right : # too far to the right
            scroll.x = self.screen_bounds.rect.right - self.rect.right
            self.rect.right = self.screen_bounds.rect.right
            #print "Scrolling right, screen right bound of %d exceeded"%self.screen_bounds.rect.right
            
        elif self.rect.left < self.screen_bounds.rect.left: # too far to the left
            scroll.x = self.screen_bounds.rect.left - self.rect.left
            self.rect.left = self.screen_bounds.rect.left
            #print "Scrolling left"
            
        # scrolling level 
        self.level.scroll(scroll)
            
    def move_x(self,step):
        
        self.incr.x = step
        print "Moving step lenght of  %d"%(step)
        
        
    def jump(self):
        
        # check for platform below
        self.rect.y += Player.PLATFORM_CHECK_STEP
        platforms = pygame.sprite.spritecollide(self,self.level.platforms,False)
        self.rect.y -= Player.PLATFORM_CHECK_STEP
        
        if (len(platforms) > 0) :
            self.incr.y = Player.JUMP_SPEED
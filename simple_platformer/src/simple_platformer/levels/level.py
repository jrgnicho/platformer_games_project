import pygame

from simple_platformer.utilities import Vector2D, ScreenBounds
from simple_platformer.utilities import Colors, ScreenProperties
from simple_platformer.levels import Platform

class Level():
    
    def __init__(self):
        
        self.platforms = pygame.sprite.Group()
        self.enemys  = pygame.sprite.Group()
        
        self.scroll_shift = Vector2D()
        self.min_bounds = Vector2D(0,0)
        self.max_bounds = Vector2D(ScreenProperties.SCREEN_WIDTH*3,ScreenProperties.SCREEN_HEIGHT*4)
        
        self.rect = pygame.Rect(0,0,self.max_bounds.x - self.min_bounds.x,
                                self.max_bounds.y - self.min_bounds.y)   
        
        
    def set_platforms(self,platforms):
        
        # place platforms relative to level
        for p in platforms:
            
            if type(p) is Platform: 
                p.rect.centerx = p.rect.centerx + self.rect.x  
                p.rect.centery = self.rect.centery -  p.rect.y                         
                self.platforms.add(p) 
            #endif                
        #endfor   
        
        
    def update(self):
        
        self.platforms.update()
        self.enemys.update()
        
    def draw(self,screen):
        
        # draw background
        screen.fill(Colors.BLUE)

        # draw objects
        self.platforms.draw(screen)
        self.enemys.draw(screen)
        
    def scroll(self,incr):
        """ Shifts the world and its objects by incr """
        """ inputs:"""
        """     - incr: Vector2D() value in world coordinates """
        #if (abs(incr.x) > 0) or (abs(incr.y) > 0):        
        #    print "Scrolling world by x: %d, y: %d"%(incr.x,incr.y)
        
        self.rect.x += incr.x
        self.rect.y -= incr.y
        
        for platform in self.platforms:
            platform.rect.x += incr.x
            platform.rect.y -= incr.y
        #endfor
        
        for enemy in self.enemys:
            enemy.rect.x += incr.x
            enemy.rect.y -= incr.y
        #endfor       
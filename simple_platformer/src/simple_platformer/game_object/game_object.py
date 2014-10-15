import pygame
from pygame.sprite import Sprite

class GameObject(Sprite):
                
    
    def __init__(self,centerx,centery,w,h,parent_object = None):
        Sprite.__init__(self)
        self.parent_object = parent_object
        self.rect = pygame.Rect(0,0,w,h)
        self.rect.centerx = centerx
        self.rect.centery = centery
        
    @property
    def screen_x(self):
        sx = 0;
        if self.parent_object != None:
            sx = self.rect.x + self.parent_object.screen_x
        else:
            sx = self.rect.x            
        #endif
        
        return sx 
    
    @property
    def screen_y(self):
        sy = 0
        if self.parent_object != None:
            sy = self.rect.y + self.parent_object.screen_y
        else:
            sy = self.rect.y            
        #endif
                
        return sy
    
    @property
    def screen_bottom(self):
        return self.rect.height + self.screen_y()
        
    @property
    def screen_top(self):
        return -self.rect.height + self.screen_y()
    
    @property
    def screen_left(self):
        return self.screen_x()
    
    @property
    def screen_right(self):
        return self.screen_x + self.rect.width
    
    @property
    def screen_centerx(self):
        return self.rect.centerx + self.screen_x()
    
    @property
    def screen_centery(self):
        return self.rect.centery + self.screen_y()
            
    
    
        
    
        
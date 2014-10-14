import pygame
from pygame.sprite import Sprite

class GameObject(Sprite):
    
    class GameRectangle(pygame.Rect):
        
        """
        This class is a variant of the pygame.Rect class which reimplements the properties
        top and bottom so that it is in accordance with an y axis pointing up instead
        of down as it is the case for the regular pygame.Rect class.  This will allow 
        keeping the location of objects relative to a world (level) frame of reference
         instead of screen coordinate system which is more difficult to maintain
        """
        
        def __init__(self,top,left,width,height):
            pygame.Rect.__init__(self,top,left,width,height)
            
#         @property
#         def top(self):
#             return self.centery + int(0.5*self.height)
#             return self.y
#         
#         @top.setter
#         def top(self,value):
#             self.centery = value - int(0.5*self.height)
#             self.y = value
#             
#         @property
#         def bottom(self):
#             return self.centery - int(0.5*self.height)
#             return self.y - self.height
#         
#         @bottom.setter
#         def bottom(self,value):
#             self.centery = value + int(0.5*self.height)
#             self.y = value + self.height            
#             print "Bottom set to %i, top at %i"%(value,self.top)
            
    
    def __init__(self,centerx,centery,w,h,parent_object = None):
        Sprite.__init__(self)
        self.parent_object = parent_object
        self.rect = GameObject.GameRectangle(0,0,w,h)
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
        return self.rect.height + self.screen_y
        
    @property
    def screen_top(self):
        return -self.rect.height + self.screen_y
    
    @property
    def screen_left(self):
        return self.screen_x
    
    @property
    def screen_right(self):
        return self.screen_x + self.rect.width
    
    
        
    
        
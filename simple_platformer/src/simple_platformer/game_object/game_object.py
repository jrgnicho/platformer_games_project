import pygame
from pygame.sprite import Sprite
from simple_platformer.utilities import Colors
from simple_platformer.game_object import CollisionMasks

class GameObject(Sprite):  
    
    def __init__(self,x = 0,y = 0,w = 40,h = 60 ,parent_object = None):
        Sprite.__init__(self)
        self.parent_object = parent_object if parent_object != self else None
        self.target_object = None # reserverd for another instance of GameObject
        self.__rect__ = pygame.Rect(x,y,w,h)
        self.__half_width__ = int(0.5*self.__rect__.width) 
        self.__half_height__ = int(0.5*self.__rect__.height)
        self.collision_bitmask = CollisionMasks.DEFAULT
        self.type_bitmask = CollisionMasks.DEFAULT
        
        # drawing
        self.drawable_sprite = pygame.sprite.Sprite()
        self.drawable_sprite.image = pygame.Surface([w,h])
        self.drawable_sprite.image.fill(Colors.RED)
        self.drawable_sprite.rect = self.drawable_sprite.image.get_rect()
        self.drawable_group = pygame.sprite.Group()
        self.drawable_group.add(self.drawable_sprite)
        
        # collision detection support        
        self.__range_collision_group__ = pygame.sprite.Group()    
        self.nearby_platforms = pygame.sprite.Group()
        
    def draw(self,screen):            
        self.drawable_group.draw(screen)
        
    def update(self):        
        self.drawable_sprite.rect.x = self.screen_x
        self.drawable_sprite.rect.y = self.screen_y
       
    @property
    def range_collision_group(self):
        
        for sp in iter(self.__range_collision_group__):
            sp.rect.center = self.__rect__.center
        #endfor
        
        return self.__range_collision_group__
        
        
    @property
    def rect(self):
        return self.__rect__
    
    @rect.setter
    def rect(self,r):        
        if r is not None:
            self.__rect__ = r
            self.__half_width__ = int(0.5*self.__rect__.width) 
            self.__half_height__ = int(0.5*self.__rect__.height)
        #endif
        
    @property
    def x(self):
        if self.parent_object is None:            
            return self.__rect__.x
        else:            
            return self.__rect__.x + self.parent_object.x
        #endif
        
    @property
    def centerx(self):
        if self.parent_object is None:            
            return self.__rect__.centerx
        else:            
            return self.__rect__.centerx + self.parent_object.x
        #end
        
    @property
    def y(self):
        if self.parent_object is None:            
            return self.__rect__.y
        else:            
            return self.__rect__.y + self.parent_object.y
        #endif
        
    @property    
    def centery(self):
        if self.parent_object is None:
            return self.__rect__.centery
        else:
            return self.__rect__.centery + self.parent_object.y
        
    @property
    def width(self):        
        if self.__rect__ is not None:
            return self.__rect__.width
        else:
            return -1
        #endif
        
    @width.setter
    def width(self,w):        
        self.__rect__.width = w
        self.__half_width__ = int(0.5*w)
        
    @property
    def height(self):        
        if self.__rect__ is not None:
            return self.__rect__.height
        else:
            return -1
        #endif        
        
    @height.setter
    def height(self,h):
        self.__rect__.height = h
        self.__half_height__ = int(0.5*h)
        
        
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
        return self.screen_y
    
    @property
    def screen_left(self):
        return self.screen_x 
    
    @property
    def screen_right(self):
        return self.screen_x + self.rect.width
    
    @property
    def screen_centerx(self):
        return self.__half_width__ + self.screen_x
    
    @property
    def screen_centery(self):
        return self.__half_height__ + self.screen_y    

            
            
    
    
        
    
        
import pygame
import os
from pygame.sprite import Sprite
from pygame.sprite import Group
from game_assets.properties import HitProperties
from game_assets.properties import LayerDrawPriorityTypes

class AnimationAssets(object):
    
    def __init__(self):
        
        self.sprites_left = []
        self.sprites_right = []
        self.frame_rate = 0
        self.layer_drawing_priority = LayerDrawPriorityTypes.PLAYER_LAYER
        
        
class CollisionSpriteGroup(pygame.sprite.Sprite):
    
    """
    TODO
        add properties to modify the center and rect objects 
    """
    
    def __init__(self):
        
        Sprite.__init__(self)
        
        # bounding rectangle for all the sprites in this 
        self.sprites = pygame.sprite.Group()
        self.rect = pygame.Rect(0,0,0,0) # bounding rectangle for all the rectangles in this group

    def get_rect(self):
        return self.__rect


    def set_rect(self, value):
        self.__rect = value


    def del_rect(self):
        del self.__rect

        
    def compute_bounding_rect(self):
        """
        Computes the bounding rectangle that contains all the sprites in this group and assigns it to self.rect
        """
        pass
        
    def add(self,sprite):
        
        self.sprites.add(sprite)
        self.compute_bounding_rect()
        
    rect = property(get_rect, set_rect, del_rect, "rect's docstring")
        
class HitCollisionGroup(CollisionSpriteGroup,HitProperties):
    
    def __init__(self):
        
        CollisionSpriteGroup.__init__(self)
        HitProperties.__init__(self)
        
        
class AttackCollisionAssets(object):
    
    """
        Class that servers as a container for list of HitCollisionGroup objects for the left and right orientations
    """
    
    def __init__(self):
        
        self.hits_left =[] # list of HitCollisionGroup objects
        self.hits_right =[]
        
    def add_group(self,left_group,right_group):
        self.hits_left.append(left_group)
        self.hits_right.append(right_group)
        
    def len(self):
        
        return len(self.hits_left)
        
    
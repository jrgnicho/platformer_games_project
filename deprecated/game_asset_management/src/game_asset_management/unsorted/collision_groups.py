"""
This will be used eventually to perform group collisions 
"""

import pygame
import os
from pygame.sprite import Sprite
from pygame.sprite import Group
from game_asset_management.properties import HitProperties
from game_asset_management.properties import DrawLayerPriorities
from game_asset_management.properties import CollisionBitMasks as CM

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
        self.collision_type_mask =CM.PLAYER
        self.collision_with_mask = CM.PLATFORMS | CM.POWERUPS | CM.ENEMIES

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
import pygame
import os
from pygame.sprite import Sprite
from pygame.sprite import Group
from game_assets.properties import HitProperties
from game_assets.properties import DrawLayerPriorities
from game_assets.properties import CollisionBitMasks as CM

class SpritesAsset(object):
    
    def __init__(self):
        
        self.image_file = ''
        self.cols = 1
        self.rows = 1
        self.flipx = False
        self.flipy = False

class AnimationAssets(object):
    
    def __init__(self):
    
        self.sprites_left = SpritesAsset()
        self.sprites_right = SpritesAsset()
        self.frame_rate = 0
        self.layer_drawing_priority = DrawLayerPriorities.PLAYER_LAYER
        
class CollisionAssets(object):
    
    def __init__(self):
        
        self.rectangles = []
        self.collision_type_mask =CM.PLAYER
        self.collision_with_mask = CM.PLATFORMS | CM.POWERUPS | CM.ENEMIES
        
class HitAssets(CollisionAssets,HitProperties):
    
    def __init__(self):
        CollisionAssets.__init__(self)
        HitProperties.__init__(self)     
        
        
    
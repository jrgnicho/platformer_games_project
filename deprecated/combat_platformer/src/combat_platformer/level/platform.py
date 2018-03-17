import pygame

from simple_platformer.utilities import Colors
from simple_platformer.game_object import GameObject

class Platform(GameObject):
    
    def __init__(self,x,y,w,h):
        
        GameObject.__init__(self,x,y,w,h)
        self.drawable_sprite.image.fill(Colors.GREEN)
        


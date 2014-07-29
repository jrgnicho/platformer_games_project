
import pygame
import constants
from simple_platformer.utilities import *


class Vector2D:
        
    def __init__(self,x = 0,y = 0):
        
        self.x = x
        self.y = y
        
class ScreenBounds(pygame.sprite.Sprite):
    
    
    def __init__(self,
                 x = 0.25*ScreenProperties.SCREEN_WIDTH,
                 y = 0.2*ScreenProperties.SCREEN_HEIGHT,
                 w = 0.5*ScreenProperties.SCREEN_WIDTH,
                 h = 0.6*ScreenProperties.SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)   
        
        self.rect = pygame.Rect(x,y,w,h)
        
import pygame

from simple_platformer.utilities import ScreenBounds
from simple_platformer.utilities import Colors, ScreenProperties

class Platform(pygame.sprite.Sprite):
    
    def __init__(self,x,y,w,h):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([w,h])
        self.image.fill(Colors.GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y            



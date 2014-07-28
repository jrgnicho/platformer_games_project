
import pygame
import constants


class Vector2D:
        
    def __init__(self,x = 0,y = 0):
        
        self.x = x
        self.y = y
        
class ScreenBounds(pygame.sprite.Sprite):
    
    
    def __init__(self,x= 150,y=100,w = 500,h =400):
        pygame.sprite.Sprite.__init__(self)   
        
        self.rect = pygame.Rect(x,y,w,h)
        
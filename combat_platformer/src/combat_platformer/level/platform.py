import pygame

from simple_platformer.utilities import Colors
from simple_platformer.game_object import GameObject

class Platform(GameObject):
    
    def __init__(self,x,y,w,h):
        
        GameObject.__init__(self,x,y,w,h)
        self.drawable_sprite = pygame.sprite.Sprite()
        self.drawable_sprite.image = pygame.Surface([w,h])
        self.drawable_sprite.image.fill(Colors.GREEN) 
        self.drawable_sprite.rect = self.drawable_sprite.image.get_rect()  
        
    def update(self):
        
        self.drawable_sprite.rect.x = self.screen_x
        self.drawable_sprite.rect.y = self.screen_y
        


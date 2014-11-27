import pygame

class AnimationSprite(pygame.sprite.Sprite):
    
    """
    AnimationSprite:
        - Extends pygame Sprite in order to include an offset (x,y) that will be used to
            draw the image relative to a parent object which should also have a 'rect' property.
            During a draw, the 'rect' property of the class will be place as follows:
            x = parent.rect.centerx + offset(0)
            y = parent.rect.bottom + offset(1) 
    """
    
    def __init__(self,image,offset = (0,0) ,parent = None):
        
        pygame.sprite.Sprite.__init__(self)
        
        self.parent = parent
        self.image = image
        self.__rect__= image.get_rect()
        self.offset = offset
        
    @rect.setter   
    def rect(self):
        
        self.__rect__.centerx = (self.parent.rect.centerx if self.parent != None else 0) + self.offset[0]
        self.__rect__.bottom = (self.parent.rect.bottom if self.parent != None else 0) + self.offset[1]
        return self.__rect__
import pygame

class AnimationSprite(pygame.sprite.Sprite):
    
    """
    AnimationSprite:
        - Extends pygame Sprite in order to include an offset (x,y) that will be used to
            draw the image
    """
    
    def __init__(self,image,offset = (0,0) ):
        
        pygame.sprite.Sprite.__init__(self)
        
        self.__image__ = image
        self.__rect__= image.get_rect()
        self.offset = offset
   
    def set_from(self,sp):
        """
        set_from(sp) -> None
            - Copies all members from input AnimationSprite 'sp' 
        """ 
        
        self.image = sp.image
        self.offset = sp.offset
    
    @property
    def bottom(self):
        return self.__rect__.bottom    
        
    @bottom.setter
    def bottom(self,val):
        self.__rect__.bottom = val + self.offset[1]
    
    @property
    def centerx(self):
        return self.__rect__.centerx
        
    @centerx.setter
    def centerx(self,val):
        self.__rect__.centerx = val + self.offset[0]        
        
    @property
    def image(self):
        return self.__image__
    
    @image.setter
    def image(self,im):
        self.__image__ = im
        self.__rect__ = im.get_rect()
        
    @property   
    def rect(self):
        
        return self.__rect__
    
    def invert(self,xflip = True,yflip = False):
        
        offsetx = -self.offset[0] if xflip else self.offset[0]
        offsety = -self.offset[1] if yflip else self.offset[1]
        return AnimationSprite(pygame.transform.flip(self.__image__,xflip,yflip),(offsetx,offsety))
        
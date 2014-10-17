import pygame
from combat_platformer.player import PlayerBase
from combat_platformer.enemy import EnemyProperties

class EnemyBase(PlayerBase):
    
    def __init__(self):
        PlayerBase.__init__(self)
        self.properties = EnemyProperties()
        self.target_object = None
        
    def setup(self):
        
        # collision sprite
        self.rect = pygame.Rect(0,0,self.properties.collision_width,
                                                 self.properties.collision_height)    
        
        self.max_delta_x = self.properties.max_step_x  
        
        if self.target_object == None:
            print "The 'target_object' member in the EnemyBase class has not been set"
            return False
        #endif
        
        
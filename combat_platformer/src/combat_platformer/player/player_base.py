from simple_platformer.game_object import *
from simple_platformer.game_object import CollisionMasks
from combat_platformer.player import PlayerProperties

class PlayerBase(AnimatableObject):
    
    def __init__(self):
        
        AnimatableObject.__init__(self)
        
        # player properties
        self.properties = PlayerProperties()
        
        # movement 
        self.vertical_speed = 0
        self.horizontal_speed = 0   
        self.momentum = 0  #"amount of resistance to change in velocity"
        
        
        # auxilary properties
        self.max_delta_x = 0;
        self.momentum_reduction = 0
        self.midair_dash_remaining = 0
        self.active_attacks = []
        
        # collision masks
        self.collision_bitmask = CollisionMasks.ENEMY
        self.type_bitmask = CollisionMasks.PLAYER
        
        
    def setup(self,assets):
        
        # collision detection objects
        self.rect = pygame.Rect(0,0,self.properties.collision_width,
                                                 self.properties.collision_height)          
        
        # auxilary properties
        self.midair_dash_remaining = self.properties.max_midair_dashes
        
        self.max_delta_x = self.properties.max_step_x
        self.momentum_reduction = self.properties.inertial_reduction
        
        return True
        
    def turn_right(self,dx):        
        self.facing_right = True
        self.horizontal_speed= dx
        
    def turn_left(self,dx):        
        self.facing_right = False
        self.horizontal_speed= dx   
        
        
    def set_horizontal_speed(self,speed):
        if self.facing_right:
            self.horizontal_speed = speed
        else:
            self.horizontal_speed = -speed  
            
        #endif 
        
    def apply_gravity(self,g ):    
            
        self.vertical_speed+= g   
        
    def set_vertical_speed(self,s):
        
        self.vertical_speed = s
        
        
    def set_momentum(self,momentum):
        if self.facing_right:
            self.momentum = momentum
        else:
            self.momentum = -momentum
            
            
    def step_momentum(self):
        
        if self.momentum>0 :
                            
            # reduce inertia
            self.momentum-=self.momentum_reduction          
            
            if self.momentum < 0:
                self.momentum = 0
                
        elif self.momentum < 0 :
                            
            # reduce inertia
            self.momentum+=self.momentum_reduction 
            
            if self.momentum > 0:
                self.momentum = 0                
            #endif
            
        #endif
            
    def step_x(self):
        
        dx = self.horizontal_speed
                
        if dx > self.max_delta_x:
            dx = self.max_delta_x
        elif dx < -self.max_delta_x:
            dx = -self.max_delta_x
                        
        #endif
               
        self.__rect__.centerx+=dx
    
    def step_y(self):
        
        self.__rect__.centery+=self.vertical_speed       
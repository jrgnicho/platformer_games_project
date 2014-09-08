from simple_platformer.animatable_object import *
from simple_platformer.players import PlayerProperties

class PlayerBase(AnimatableObject):
    
    def __init__(self):
        
        AnimatableObject.__init__(self)
        
        # player properties
        self.player_properties = PlayerProperties()
        
        # movement 
        self.vertical_speed = 0
        self.horizontal_speed = 0   
        self.momentum = 0  #"amount of resistance to change in velocity"
                               
        
        # collision detection objects
        self.collision_sprite.rect = pygame.Rect(0,0,self.player_properties.collision_width,
                                                 self.player_properties.collision_height)  
        
        
        # auxilary properties
        self.midair_dash_counter = self.player_properties.max_midair_dashes
        self.range_collision_group = pygame.sprite.Group()    
        self.nearby_platforms = pygame.sprite.Group()
        self.active_attacks = []
        
        
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
            
            
    def update_momentum(self):
        
        if self.momentum>0 :
                            
            # reduce inertia
            self.momentum-=self.player_properties.inertial_reduction           
            
            if self.momentum < 0:
                self.momentum = 0
                
        elif self.momentum < 0 :
                            
            # reduce inertia
            self.momentum+=self.player_properties.inertial_reduction  
            
            if self.momentum > 0:
                self.momentum = 0
                
            #endif
            
        #endif
            
    def update_pos_x(self):
        
        dx = self.horizontal_speed+ self.momentum
        self.update_momentum()
        
        if dx > self.player_properties.max_x_position_change:
            dx = self.player_properties.max_x_position_change
        elif dx < -self.player_properties.max_x_position_change:
            dx = -self.player_properties.max_x_position_change
                        
        #endif
               
        self.collision_sprite.rect.centerx+=dx
    
    def update_pos_y(self):
        
        self.collision_sprite.rect.centery+=self.vertical_speed       
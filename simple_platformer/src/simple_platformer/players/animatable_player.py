import pygame
from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.game_state_machine import ActionKeys
from simple_platformer.utilities import GameProperties
from simple_platformer.utilities import SpriteLoader
from simple_platformer.players import PlayerProperties

class AnimatablePlayer(AnimatableObject):

    
    def __init__(self):
        
        # superclass constructor
        AnimatableObject.__init__(self)
        
        # player properties
        self.player_properties = PlayerProperties()
        
        # movement 
        self.current_upward_speed = 0
        self.current_forward_speed = 0   
        self.current_inertia = 0  #"amount of resistance to change in velocity"
                        
        # utility class for loading sprites        
        self.sprite_loader = SpriteLoader() 
        
        # midair dashing
        self.midair_dash_countdown = 1
        
        # collision detection objects
        self.collision_sprite.rect = pygame.Rect(0,0,self.player_properties.collision_width,
                                                 self.player_properties.collision_height)  
        
        self.range_collision_group = pygame.sprite.Group()    
        self.near_platforms = pygame.sprite.Group()
          
        
    def dash(self,action_key = ActionKeys.DASH): 
        
       self.set_current_animation_key(action_key),
       self.set_forward_speed(self.player_properties.dash_speed)
       
    def dash_break(self,inertia, action_key = ActionKeys.DASH_BREAK):
        
        self.set_inertia(inertia)
        self.set_forward_speed(0),
        self.set_current_animation_key(action_key)
       
    def midair_dash(self,action_key = ActionKeys.MIDAIR_DASH):
        
       self.set_current_animation_key(action_key),
       self.set_forward_speed(self.player_properties.dash_speed)
       self.set_upward_speed(0)
       self.midair_dash_countdown -=1
        
    def set_inertia(self,inertia):
        if self.facing_right:
            self.current_inertia = inertia
        else:
            self.current_inertia = -inertia             
         
        
    def set_forward_speed(self,speed):
        if self.facing_right:
            self.current_forward_speed = speed
        else:
            self.current_forward_speed = -speed  
            
        #endif 
        
    def increment_forward_speed(self,speed): 
        
        if self.facing_right:
            self.current_forward_speed += speed
        else:
            self.current_forward_speed -= speed  
            
        #endif 
    def set_upward_speed(self,s):
        self.current_upward_speed = s  

            
    def apply_gravity(self,g = GameProperties.GRAVITY_ACCELERATION):    
            
        self.current_upward_speed += g   
        
        
    def consume_inertia_residual(self):
        
        if self.current_inertia>0 :
                            
            # reduce inertia
            self.current_inertia-=self.player_properties.inertial_reduction           
            
            if self.current_inertia < 0:
                self.current_inertia = 0
                
        elif self.current_inertia < 0 :
                            
            # reduce inertia
            self.current_inertia+=self.player_properties.inertial_reduction  
            
            if self.current_inertia > 0:
                self.current_inertia = 0
                
            #endif
            
        #endif
        
                
    def compute_change_in_x(self):
        
        dx = self.current_forward_speed + self.current_inertia
        self.consume_inertia_residual()
        
        if dx > self.player_properties.max_x_position_change:
            dx = self.player_properties.max_x_position_change
        elif dx < -self.player_properties.max_x_position_change:
            dx = -self.player_properties.max_x_position_change
                        
        #endif
               
        return dx
    
    def compute_change_in_y(self):
        
        return self.current_upward_speed        
        
            
    def turn_right(self,dx):        
        self.facing_right = True
        self.current_forward_speed = dx
        
    def turn_left(self,dx):        
        self.facing_right = False
        self.current_forward_speed = dx          
            
        
    def setup(self,sprites_desc_file):
        
        action_keys = [ActionKeys.STAND,
                       ActionKeys.RUN ,
                       ActionKeys.JUMP,
                       ActionKeys.FALL,
                       ActionKeys.LAND,
                       ActionKeys.STAND_EDGE,
                       ActionKeys.DASH_BREAK,
                       #ActionKeys.ATTACK,
                       ActionKeys.HANG,
                       ActionKeys.DASH,
                       ActionKeys.CLIMB,
                       ActionKeys.MIDAIR_DASH]
        
        return self.load_sprites(sprites_desc_file,action_keys)
        
    def load_sprites(self,sprites_desc_file,action_keys):
        
        if self.sprite_loader.load_sets(sprites_desc_file):
            print "Sprites successfully loaded"
        else:
            print "Sprites failed to load"
            return False
        
        #endif
        
        for key in action_keys:
            
            if (not self.add_animation_sets(key,self.sprite_loader.sprite_sets[key],
                                                    self.sprite_loader.sprite_sets[key].invert_set())) :
                print "Error loading animation for action key %s"%(key)
                return False
            #endif
            
        #endfor
        
        print "Added all sprite sets"

        return True
import pygame
from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.game_state_machine import ActionKeys
from simple_platformer.utilities import GameProperties
from simple_platformer.utilities import SpriteLoader

class AnimatablePlayer(AnimatableObject):
    
    JUMP_SPEED = -10 # y axis points downwards
    SUPER_JUMP_SPEED = -12
    RUN_SPEED = 4
    DASH_SPEED = 8       
    STAND_DISTANCE_FROM_EDGE_THRESHOLD = 0.80 # percentage of width
    FALL_DISTANCE_FROM_EDGE_THRESHOLD = 0.40     # percentage of width

    
    def __init__(self):
        
        # superclass constructor
        AnimatableObject.__init__(self)
        
        # movement variables 
        self.current_upward_speed = 0
        self.current_forward_speed = 0   
        self.current_inertia = 0  #"amount of resistance to change in velocity"
        self.mass = 1
        
        # position change
        self.dx = 0
        self.dy = 0
                
        # utility class for loading sprites        
        self.sprite_loader = SpriteLoader() 
        
        

        
    def jump(self,action_key = ActionKeys.JUMP):
        
        self.current_upward_speed = AnimatablePlayer.JUMP_SPEED
        self.set_current_animation_key(action_key)
        
    def run(self,action_key = ActionKeys.RUN):
        
        self.current_upward_speed = 0
        if self.facing_right:
            self.current_forward_speed = AnimatablePlayer.RUN_SPEED
        else:
            self.current_forward_speed = -AnimatablePlayer.RUN_SPEED   
        #endif
        
        self.set_current_animation_key(action_key)   
        
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
        self.dy = self.current_upward_speed
        
    def apply_inertia(self,inertia_reduction = GameProperties.INERTIA_REDUCTION):
        
        if self.current_inertia != 0:
        
            self.current_forward_speed = self.current_inertia
            
            if self.current_inertia>0 :
                                
                # reduce inertia
                self.current_inertia-=inertia_reduction            
                
                if self.current_inertia < 0:
                    self.current_inertia = 0
                    
            elif self.current_inertia < 0 :
                                
                # reduce inertia
                self.current_inertia+=inertia_reduction
                
                if self.current_inertia > 0:
                    self.current_inertia = 0
                    
                #endif
                
            #endif
            
                    
        #endif
                
            
    def land(self,action_key = ActionKeys.LAND):
        
        self.current_upward_speed = 0
        self.current_forward_speed = 0
        self.set_current_animation_key(action_key)
        
                
    def compute_change_in_x(self):
               
        return self.current_forward_speed
    
    def compute_change_in_y(self):
        
        return self.current_upward_speed        
        
            
    def turn_right(self,dx):        
        self.facing_right = True
        self.current_forward_speed = dx
        
    def turn_left(self,dx):        
        self.facing_right = False
        self.current_forward_speed = dx
            
    def stand(self,action_key = ActionKeys.STAND):
        self.current_forward_speed =0
        self.set_current_animation_key(action_key)
        
    def cancel_move(self):
        self.current_forward_speed =0     
        
    def cancel_jump(self):
        if self.current_upward_speed < 0: 
            self.current_upward_speed = 0 
            
    def fall(self,action_key = ActionKeys.FALL):
        
        self.current_upward_speed = 0
        self.set_current_animation_key(action_key)
        
    def setup(self,sprites_desc_file):
        
        action_keys = [ActionKeys.STAND,
                       ActionKeys.RUN ,
                       ActionKeys.JUMP,
                       ActionKeys.FALL,
                       ActionKeys.LAND,
                       ActionKeys.STAND_EDGE,
                       ActionKeys.DASH_BREAK,
                       #ActionKeys.ATTACK,
                       ActionKeys.DASH,
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
import pygame
from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.game_state_machine import ActionKeys
from simple_platformer.utilities import GameProperties

class AnimatablePlayer(AnimatableObject):
    
    JUMP_SPEED = -10 # y axis points downwards
    SUPER_JUMP_SPEED = -12
    RUN_SPEED = 4    

    
    def __init__(self):
        
        # superclass constructor
        AnimatableObject.__init__(self)
        
        # jump speed
        self.current_upward_speed = 0
        self.current_forward_speed = 0           

        
    def jump(self,action_key = ActionKeys.JUMP):
        
        self.current_upward_speed = AnimatablePlayer.JUMP_SPEED
        self.set_current_animation_key(action_key)
        
    def run(self,facing_right,action_key = ActionKeys.RUN):
        
        self.current_upward_speed = 0
        if facing_right:
            self.facing_right = True
            self.current_forward_speed = AnimatablePlayer.RUN_SPEED
        else:
            self.facing_right = False
            self.current_forward_speed = -AnimatablePlayer.RUN_SPEED   
        #endif
        
        self.set_current_animation_key(action_key)         
            
    def apply_gravity(self,dy = GameProperties.GRAVITY_ACCELERATION):        
        self.current_upward_speed += dy
            
    def land(self,action_key = ActionKeys.LAND):
        
        self.current_upward_speed = 0
        self.current_forward_speed = 0
        self.set_current_animation_key(action_key)
        
    def apply_inertia(self,toward_right,deceleration_rate):
        
        if facing_right:
            self.facing_right = True
            self.current_forward_speed +=deceleration_rate
        else:
            self.facing_right = False
            self.current_forward_speed -=deceleration_rate
            
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
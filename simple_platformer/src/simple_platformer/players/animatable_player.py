import pygame
from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.game_state_machine import ActionKeys
from simple_platformer.utilities import GameProperties

class AnimatablePlayer(AnimatableObject):
    
    JUMP_SPEED = -10 # y axis points downwards
    SUPER_JUMP_SPEED = -12
    RUN_SPEED = 3.5
    
    def __init__(self):
        
        # superclass constructor
        AnimatableObject.__init(self)
        
        # jump speed
        self.current_upward_speed = 0
        self.current_forward_speed = 0        
        
    def jump(self,action_key = ActionsKeys.JUMP):
        
        self.current_upward_speed = AnimatablePlayer.JUMP_SPEED
        self.set_current_animation_key(action_key)
        
    def run(self,facing_right,action_key = ActionKeys.RUN):
        
        if facing_right:
            self.facing_right = True
            self.current_forward_speed = AnimatablePlayer.RUN_SPEED
        else:
            self.facing_right = False
            self.current_forward_speed = -AnimatablePlayer.RUN_SPEED            
            
    def apply_gravity(self,dy = GameProperties.GRAVITY_ACCELERATION):        
        self.current_forward_speed += dy
            
    def land(self,action_key = ActionKeys.LAND):
        
        self.current_upward_speed = 0
        self.set_current_animation_key(action_key)
        
    def apply_inertia(self,toward_right,deceleration_rate):
        
        if facing_right:
            self.current_forward_speed +=deceleration_rate
            self.turn_right(0)
        else:
            self.current_forward_speed -=deceleration_rate
            self.turn_left(0)
            
    def stand(self,action_key = ActionKeys.STAND):
        self.current_forward_speed =0
        self.set_current_animation_key(action_key)
        
            
    def fall(self,action_key = ActionKey.FALL):
        
        self.current_upward_speed = 0
        self.set_current_animation_key(action_key)
import pygame
from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.game_state_machine import ActionKeys
from simple_platformer.utilities import GameProperties
from simple_platformer.utilities import SpriteLoader

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
        
        # utility class for loading sprites        
        self.sprite_loader = SpriteLoader()      

        
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
        
    def setup(self,sprites_desc_file):
        
        return self.load_sprites(sprites_desc_file)
        
    def load_sprites(self,sprites_desc_file):
        
        if self.sprite_loader.load_sets(sprites_desc_file):
            print "Sprites successfully loaded"
        else:
            print "Sprites failed to load"
            return False
        
        #endif
        
        # adding animations to player
        if (self.add_animation_sets(ActionKeys.RUN,self.sprite_loader.sprite_sets[ActionKeys.RUN],
                                                    self.sprite_loader.sprite_sets[ActionKeys.RUN].invert_set()) and
            
            self.add_animation_sets(ActionKeys.STAND,self.sprite_loader.sprite_sets[ActionKeys.STAND],
                                                    self.sprite_loader.sprite_sets[ActionKeys.STAND].invert_set()) and
            
            self.add_animation_sets(ActionKeys.JUMP,self.sprite_loader.sprite_sets[ActionKeys.JUMP],
                                                    self.sprite_loader.sprite_sets[ActionKeys.JUMP].invert_set()) and
            
            self.add_animation_sets(ActionKeys.FALL,self.sprite_loader.sprite_sets[ActionKeys.FALL],
                                                    self.sprite_loader.sprite_sets[ActionKeys.FALL].invert_set()) and
            
            self.add_animation_sets(ActionKeys.LAND,self.sprite_loader.sprite_sets[ActionKeys.LAND],
                                                    self.sprite_loader.sprite_sets[ActionKeys.LAND].invert_set()) and
            
            self.add_animation_sets(ActionKeys.ATTACK,self.sprite_loader.sprite_sets["ATTACK_SLASH"],
                                                    self.sprite_loader.sprite_sets["ATTACK_SLASH"].invert_set())) :
            
            print "Added all sprite sets"
        else:
            return False
        
        return True
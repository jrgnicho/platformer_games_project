#!/usr/bin/env python

import pygame
from simple_platformer.levels import GameLevel, Platform
from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.players import AnimatablePlayer
from simple_platformer.utilities import *
from simple_platformer.game_state_machine import *
import rospkg

class GamePlatformer:
    
    class StateKeys:
    
        NONE=""
        STANDING="STANDING"
        RUNNING="RUNNING"
        JUMPING="JUMPING"
        FALLING="FALLING"
        LANDING="LANDING"
        EXIT = "EXIT"
    
    def __init__(self):        
        
        self.player = AnimatablePlayer()
        self.level = GameLevel()
        self.level.player = self.player
        self.screen = None
        self.proceed = True
        
        # registering handler
        self.player.add_event_handler(AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED,self.action_sequence_expired_handler)
        
    def action_sequence_expired_handler(self):
            self.level.execute(ActionKeys.ACTION_SEQUENCE_EXPIRED)
        
    def exit(self):
        
        self.proceed = False
        
    def create_level(self):
        
        # create lever
        platforms = [Platform(100, 200,100, 20),
                     Platform(80, 100,100, 20),
                     Platform(400, 300,100, 20),
                     Platform(450, 20,100, 20),
                     Platform(500, 120,100, 20),
                     Platform(450 + 80, 400 + 100,100, 20),
                     Platform(450 + 400, 400 + 300,100, 20),
                     Platform(450 + 450, 400 + 20,200, 20),
                     Platform(450 + 500, 400 + 120,100, 20),
                     Platform(0,-10,2000,20)] # floor
        
        self.level.add_platforms(platforms)
        
        self.player.collision_sprite.rect.x = 300
        self.player.collision_sprite.rect.y = 30
        self.player.collision_sprite.rect.width = 42
        self.player.collision_sprite.rect.height = 75
        
    def load_resources(self):
        
        rospack = rospkg.RosPack()
        desc_file = rospack.get_path('simple_platformer') + '/resources/hiei_sprites/sprite_details.txt'
        self.sprite_loader = SpriteLoader()
        if self.sprite_loader.load_sets(desc_file):
            print "Sprites successfully loaded"
        else:
            print "Sprites failed to load"
            return False
        
        #endif
        
        # adding animations to player
        if (self.player.add_animation_sets(ActionKeys.RUN,self.sprite_loader.sprite_sets[ActionKeys.RUN],
                                                    self.sprite_loader.sprite_sets[ActionKeys.RUN].invert_set()) and
            
            self.player.add_animation_sets(ActionKeys.STAND,self.sprite_loader.sprite_sets[ActionKeys.STAND],
                                                    self.sprite_loader.sprite_sets[ActionKeys.STAND].invert_set()) and
            
            self.player.add_animation_sets(ActionKeys.JUMP,self.sprite_loader.sprite_sets[ActionKeys.JUMP],
                                                    self.sprite_loader.sprite_sets[ActionKeys.JUMP].invert_set()) and
            
            self.player.add_animation_sets(ActionKeys.FALL,self.sprite_loader.sprite_sets[ActionKeys.FALL],
                                                    self.sprite_loader.sprite_sets[ActionKeys.FALL].invert_set()) and
            
            self.player.add_animation_sets(ActionKeys.LAND,self.sprite_loader.sprite_sets[ActionKeys.LAND],
                                                    self.sprite_loader.sprite_sets[ActionKeys.LAND].invert_set()) and
            
            self.player.add_animation_sets(ActionKeys.ATTACK,self.sprite_loader.sprite_sets["ATTACK_SLASH"],
                                                    self.sprite_loader.sprite_sets["ATTACK_SLASH"].invert_set())) :
            
            print "Added all sprite sets"
        else:
            return False
        
        return True
        
    def create_transition_rules(self):
        
        # run state
        run_state = self.create_base_game_state(GamePlatformer.StateKeys.RUNNING,
                                                 AnimatablePlayer.RUN_SPEED, lambda: self.player.run(True), None)
        
        # stand state
        stand_state = self.create_base_game_state(GamePlatformer.StateKeys.STANDING,
                                                 0, lambda: self.player.stand(), None)
        
        # jump state
        jump_state = self.create_base_game_state(GamePlatformer.StateKeys.JUMPING,
                                         AnimatablePlayer.RUN_SPEED, lambda: self.player.jump(), None)
        jump_state.add_action(ActionKeys.CANCEL_MOVE,lambda : self.player.cancel_move())
        jump_state.add_action(ActionKeys.CANCEL_JUMP,lambda : self.player.cancel_jump())
        jump_state.add_action(ActionKeys.APPLY_GRAVITY,lambda : self.player.apply_gravity())
        
        # fall state
        fall_state = self.create_base_game_state(GamePlatformer.StateKeys.FALLING,
                                 AnimatablePlayer.RUN_SPEED, lambda: self.player.fall(), None)
        fall_state.add_action(ActionKeys.CANCEL_MOVE,lambda : self.player.cancel_move())
        fall_state.add_action(ActionKeys.APPLY_GRAVITY,lambda : self.player.apply_gravity())
        
        # land state
        land_state = State(GamePlatformer.StateKeys.LANDING)
        land_state.set_entry_callback(lambda : self.player.land())
        
        # exit state
        exit_state = State(GamePlatformer.StateKeys.EXIT)
        exit_state.set_entry_callback(lambda : self.exit())
        
        # transitions
        sm = self.level
        
        sm.add_transition(run_state,ActionKeys.STAND,GamePlatformer.StateKeys.STANDING)
        sm.add_transition(run_state,ActionKeys.CANCEL_MOVE,GamePlatformer.StateKeys.STANDING)
        sm.add_transition(run_state,ActionKeys.JUMP,GamePlatformer.StateKeys.JUMPING)
        sm.add_transition(run_state,ActionKeys.FALL,GamePlatformer.StateKeys.FALLING)
        sm.add_transition(run_state,ActionKeys.PLATFORM_LOST,GamePlatformer.StateKeys.FALLING)
        
        sm.add_transition(stand_state,ActionKeys.RUN,GamePlatformer.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.JUMP,GamePlatformer.StateKeys.JUMPING)
        sm.add_transition(stand_state,ActionKeys.FALL,GamePlatformer.StateKeys.FALLING)
        sm.add_transition(stand_state,ActionKeys.PLATFORM_LOST,GamePlatformer.StateKeys.FALLING)
        sm.add_transition(stand_state,ActionKeys.MOVE_LEFT,GamePlatformer.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.MOVE_RIGHT,GamePlatformer.StateKeys.RUNNING)
        
        sm.add_transition(jump_state,ActionKeys.LAND,GamePlatformer.StateKeys.LANDING)
        sm.add_transition(jump_state,ActionKeys.FALL,GamePlatformer.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_BELOW,GamePlatformer.StateKeys.LANDING)
        sm.add_transition(jump_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,GamePlatformer.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_ABOVE,GamePlatformer.StateKeys.FALLING)
        
        sm.add_transition(fall_state,ActionKeys.LAND,GamePlatformer.StateKeys.LANDING)
        sm.add_transition(fall_state,ActionKeys.COLLISION_BELOW,GamePlatformer.StateKeys.LANDING)
        
        sm.add_transition(land_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,GamePlatformer.StateKeys.STANDING)  
        sm.add_transition(land_state,ActionKeys.JUMP,GamePlatformer.StateKeys.JUMPING,
                          lambda : self.player.animation_set_progress_percentage()>0.2)  
        sm.add_transition(land_state,ActionKeys.PLATFORM_LOST,GamePlatformer.StateKeys.FALLING) 
        
        sm.add_state(exit_state)   
        
        
        
    def create_base_game_state(self,state_key,run_speed,entry_cb = None,exit_cb = None):
        
        state = State(state_key)
        state.set_entry_callback(entry_cb)
        state.set_exit_callback(exit_cb)
        
        state.add_action(ActionKeys.MOVE_LEFT,lambda : self.player.turn_left(-run_speed))
        state.add_action(ActionKeys.MOVE_RIGHT,lambda : self.player.turn_right(run_speed))
        #state.add_action(ActionKeys.APPLY_GRAVITY,lambda : self.player.apply_gravity())
        state.add_action(ActionKeys.STEP_GAME,lambda : True)
        
        self.level.add_transition(state,ActionKeys.EXIT_GAME,GamePlatformer.StateKeys.EXIT)
        
        return state
         
        
    def setup(self):
        
        if not self.load_resources():
            return False 
        self.create_level()
        self.create_transition_rules()
            
        return True
    
    def step_game(self):
        
        if (self.proceed and self.level.update()):
            self.level.draw(self.screen)            

            return True
        
        else:
            return False
    
    def run(self):
        
        pygame.init()
        
        size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Slim shady")        
        
        if not self.setup():
            print "setup failed"
            pygame.quit()
            return
        
        clock = pygame.time.Clock()
        while self.step_game():
            
            clock.tick(GameProperties.FRAME_RATE)            
            #print "miliseconds elapse " + str(pygame.time.get_ticks())            
            pygame.display.flip()
       #endwhile     
            
        
        pygame.quit()
    
if __name__ == "__main__":
    
    game = GamePlatformer()
    game.run()

        
        
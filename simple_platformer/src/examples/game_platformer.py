#!/usr/bin/env python

import pygame
from simple_platformer.levels import GameLevel, Platform
from simple_platformer.game_object import AnimatableObject
from simple_platformer.players import PlayerStateMachine
#from simple_platformer.players import AnimatablePlayer
from simple_platformer.utilities import *
from simple_platformer.game_state_machine import *
import rospkg

class GamePlatformer(object):
    
    def __init__(self):        
        
        # player 
        self.player = PlayerStateMachine()
        self.player.collision_sprite.rect.width = 42
        self.player.collision_sprite.rect.height = 75
        
        #level
        self.level = GameLevel()
        self.level.player = self.player
        self.screen = None
        self.proceed = True

    def exit(self):
        
        self.proceed = False      

        
    def load_resources(self):
        
        rospack = rospkg.RosPack()
        desc_file = rospack.get_path('simple_platformer') + '/resources/hiei_sprites/sprite_details.txt'     
        background_file = rospack.get_path('simple_platformer') + '/resources/backgrounds/cplusplus_programming_background_960x800.jpg'
        
        
        return self.level.load_background(background_file) and self.player.setup(desc_file)
          
    def setup(self):
        
        if not self.load_resources():
            return False 
        
        if not self.level.setup():
            return False
            
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
        pygame.display.set_caption("Slim shady [x: jump , z: dash, <-: left, ->: right")        
        
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

        
        
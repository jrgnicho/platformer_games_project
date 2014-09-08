#!/usr/bin/env python

import pygame
from simple_platformer.utilities import *
from simple_platformer.game_state_machine import *
from simple_platformer.levels import Platform
from combat_platformer.player import PlayerStateMachine
from combat_platformer.level import LevelBase
import rospkg

class BasicPlatformer(object):
    
    def __init__(self):        
        
        # player 
        self.player = PlayerStateMachine()
        self.player.collision_sprite.rect.width = 42
        self.player.collision_sprite.rect.height = 75
        
        #level
        self.level = LevelBase()
        self.level.player = self.player
        self.screen = None
        self.proceed = True

    def exit(self):
        
        self.proceed = False      

        
    def load_resources(self):
        
        rospack = rospkg.RosPack()   
        background_file = rospack.get_path('simple_platformer') + \
        '/resources/backgrounds/cplusplus_programming_background_960x800.jpg'        
        
        return self.level.load_background(background_file) and self.load_player_sprites()
    
    def load_player_sprites(self):
        rospack = rospkg.RosPack()
        sprites_list_file = rospack.get_path('simple_platformer') + '/resources/hiei_sprites/sprite_list.txt' 
        
          
        self.sprite_loader = SpriteLoader() 
        
        if self.sprite_loader.load_sets(sprites_list_file):
            print "Sprites successfully loaded"
        else:
            print "Sprites failed to load"
            return False
        
        #endif
        
        if not self.player.setup():
            return False
        
        keys = self.player.states_dict.keys()
        print "animation keys: " + str(keys)
        
        for key in keys:
            
            if (not self.player.add_animation_sets(key,self.sprite_loader.sprite_sets[key],
                                                    self.sprite_loader.sprite_sets[key].invert_set())) :
                print "Error loading animation for animation key %s"%(key)
                return False
            #endif
            
        #endfor
        
        print "Added all sprite sets"

        return True
          
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
        pygame.display.set_caption("Don't mess with this dragon [x: jump , z: dash, <-: left, ->: right")        
        
        if not self.setup():
            print "setup failed"
            pygame.quit()
            return
        
        clock = pygame.time.Clock()
        while self.step_game():
            
            clock.tick(GameProperties.FRAME_RATE)                     
            pygame.display.flip()
       #endwhile     
            
        
        pygame.quit()
    
if __name__ == "__main__":
    
    game = BasicPlatformer()
    game.run()

        
        
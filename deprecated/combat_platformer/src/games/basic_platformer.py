#!/usr/bin/env python

import pygame
import rospkg
from simple_platformer.utilities import *
from simple_platformer.game_state_machine import *
from combat_platformer.player import PlayerStateMachine
from combat_platformer.level import LevelBase
from combat_platformer.enemy import EnemyBase
from combat_platformer.enemy import EnemyStateMachine

RESOURCE_PACKAGE_NAME =  'simple_platformer'
PLAYER_ANIMATION_SPRITES_PATH = '/resources/hiei_sprites/animation/sprite_list.txt'
PLAYER_COLLISION_SPRITES_PATH = '/resources/hiei_sprites/collision/sprite_list.txt'

class SimpleGameAssets(object):
    
    def __init__(self):        
        self.animation_sprite_loader = SpriteLoader()
        self.collision_sprite_loader = SpriteLoader()

class BasicPlatformer(object):
    
    def __init__(self):  
        
        # assets
        self.player_assets = SimpleGameAssets()   
        self.enemy_assets = SimpleGameAssets()   
        
        # player 
        self.player = PlayerStateMachine()
        
        #level
        self.level = LevelBase()
        self.level.player = self.player
        self.screen = None
        self.proceed = True
        
        # enemys
        self.enemies_list = []        
        self.enemy_start_positions = [(200,200), (2100,50), (80,80), (3000,80),(1400,400)
                                      ,(800,-200), (1600,-300), (1200,-400), (2540,-100),(3200,-400)]  
        self.num_enemies = len(self.enemy_start_positions)
        for i in range(0,self.num_enemies):
            enemy = EnemyStateMachine()
            self.enemies_list.append(enemy)
        #endfor

    def exit(self):
        
        self.proceed = False      

        
    def load_resources(self):
        
        rospack = rospkg.RosPack()   
        background_file = rospack.get_path('simple_platformer') + \
        '/resources/backgrounds/cplusplus_programming_background_960x800.jpg'        
        
        return self.level.load_background(background_file) \
            and self.load_player_sprites()\
            and self.load_enemy_sprites()
    
    def load_player_sprites(self):
        rospack = rospkg.RosPack()
        animation_sprites_file = rospack.get_path(RESOURCE_PACKAGE_NAME) + PLAYER_ANIMATION_SPRITES_PATH
        collision_sprites_file = rospack.get_path(RESOURCE_PACKAGE_NAME) + PLAYER_COLLISION_SPRITES_PATH
        
          
        animation_sprite_loader = self.player_assets.animation_sprite_loader 
        collision_sprite_loader = self.player_assets.collision_sprite_loader 
        
        if (animation_sprite_loader.load_sets(animation_sprites_file) and 
            collision_sprite_loader.load_sets(collision_sprites_file)):
            print "Sprites successfully loaded"
        else:
            print "Sprites failed to load"
            return False
        
        #endif
        
        self.player.properties.collision_width = 42
        self.player.properties.collision_height = 75        
        if not self.player.setup(self.player_assets):       
            print "ERROR: Player setup failed"     
            return False        
        
        self.player.rect.center = (50,200)       
        
        print "Added all animation sprites"

        return True
    
    def load_enemy_sprites(self):
        
        rospack = rospkg.RosPack()
        sprite_list_file = rospack.get_path('simple_platformer') + '/resources/enemy_sprites/guardians_enemy17/sprite_list.txt'
                
        sprite_loader = self.enemy_assets.animation_sprite_loader
        sprite_loader.sprite_sets.clear()
        if sprite_loader.load_sets(sprite_list_file):
            print "Enemy sprites successfully loaded"
        else:
            print "Enemy sprites failed to load"
            return False
        #endif
        
        counter = 0
        for enemy in self.enemies_list:
            
            
            enemy.target_object = self.player
            if not enemy.setup(self.enemy_assets):
                return False
            #endif
            
            enemy.rect.center= self.enemy_start_positions[counter]
            counter+=1           
            self.level.add_enemy(enemy)
            
        #endfor
        
        return True     
    
    def setup(self):
        
        if not self.load_resources():
            return False 
             
        if not self.level.setup():
            return False
            
        return True
    
    def step_game(self,elapsed_time):
        
        if (self.proceed and self.level.update(elapsed_time)):
            self.level.draw(self.screen)            

            return True
        
        else:
            return False
    
    def run(self):
        
        pygame.init()
        
        size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(size,pygame.SWSURFACE )
        pygame.display.set_caption("Don't mess with this dragon [x: jump , z: dash, s: attack,<-: left, ->: right")        
        
        if not self.setup():
            print "setup failed"
            pygame.quit()
            return
        
        clock = pygame.time.Clock()
        while self.step_game(clock.get_time()):
            
            clock.tick(GameProperties.FRAME_RATE)                     
            pygame.display.flip()
            
       #endwhile     
        
        print str(pygame.display.Info())
        pygame.quit()
    
if __name__ == "__main__":
    
    game = BasicPlatformer()
    game.run()

        
        
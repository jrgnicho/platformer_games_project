#!/usr/bin/env python

import pygame
import rospkg
import sys
from simple_platformer.utilities import *
from simple_platformer.game_object import GameObject
from simple_platformer.game_object import AnimatableObject
from combat_platformer.attack import Attack
from combat_platformer.attack.attack import AttackGroup

RESOURCE_PACKAGE_NAME =  'simple_platformer'
ANIMATION_SPRITES_PATH = '/resources/hiei_sprites/animation/attack_list.txt'
COLLISION_SPRITES_PATH = '/resources/hiei_sprites/collision/sprite_list.txt'
SPRITE_KEYS = ['ATTACK_1', 'ATTACK_2', 'ATTACK_3']



class TestAttack(object):
    
    def __init__(self):
        
        self.sprite_loader = SpriteLoader()
        self.game_object = AnimatableObject()
        self.attacks = AttackGroup(self.game_object,{})
        
    def load_sprites(self):
        
        rospack = rospkg.RosPack()
        coll_file = rospack.get_path(RESOURCE_PACKAGE_NAME) + COLLISION_SPRITES_PATH
        #coll_file = rospack.get_path(RESOURCE_PACKAGE_NAME) + '/' + ANIMATION_SPRITES_PATH
        
        # loading collision sprites
        if self.sprite_loader.load_sets(coll_file):
            
            for k in SPRITE_KEYS:
                attack = Attack(self.game_object, (self.sprite_loader.sprite_sets[k],
                                                   self.sprite_loader.sprite_sets[k].invert_set(True,False)))
                self.attacks.add(k,attack)
            
            print "Collision sprites successfully loaded"
        else:
            print "Collision sprites failed to load"
            return False
        
        #loading animation sprites
        self.sprite_loader.clear()
        animation_file = rospack.get_path(RESOURCE_PACKAGE_NAME) + '/' + ANIMATION_SPRITES_PATH
        #animation_file = rospack.get_path(RESOURCE_PACKAGE_NAME) + COLLISION_SPRITES_PATH
        if self.sprite_loader.load_sets(animation_file):
            for k in SPRITE_KEYS:
                set = self.sprite_loader.sprite_sets[k]
                self.game_object.add_animation_sets(k,set,set.invert_set(True,False))
            #endfor
            
            print "Animation sprites successfully loaded"
        else:
            print "Animation sprites failed to load"
            return False
        #endif
        
        return True
        
    def run(self):
        
        size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Plausible deniability.")                
        
        if not self.load_sprites():
            pygame.quit() 
            return
        
        # creating background
        background = pygame.sprite.Sprite()
        background.image = pygame.Surface([ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT])
        background.image.fill(Colors.WHITE)
        background.rect = background.image.get_rect()
        
        proceed = True
        clock = pygame.time.Clock()
        key_index = 0
        print "Press N to go to next sprite sequence, SPACE to turn"
        
        # initializing game object
        key = SPRITE_KEYS[0]
        self.game_object.set_current_animation_key(key)
        self.attacks.select_attack(key)    
        
        self.game_object.rect.centerx = background.rect.centerx
        self.game_object.rect.bottom = background.rect.centery    
                
        # main loop
        while proceed:

            for event in pygame.event.get():                
                if event.type  == pygame.QUIT:
                    proceed = False
                    break                
                #endif
                
                # next animation
                if event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_ESCAPE:
                        proceed = False
                        break
                    #endif
                    
                    if event.key == pygame.K_SPACE:
                        self.game_object.facing_right = not self.game_object.facing_right
                    
                    if event.key == pygame.K_n:
                        key_index += 1
                        
                        # reset if greater that keys available
                        if key_index >= len(self.attacks):
                            key_index = 0                        
                        #endif
                        key = SPRITE_KEYS[key_index]
                        self.game_object.set_current_animation_key(key)
                        self.attacks.select_attack(key)
                        time_elapsed =  pygame.time.get_ticks()
                        
#                         print "Selected sprite set %s with %i strikes"%(SPRITE_KEYS[key_index] ,
#                                                                         self.attacks.active_attack.strikes_count())                        
                #endif
                        
            #endfor
            
            if not proceed:
                break
            #endif
            
            # updating objects
            self.game_object.update()
            self.attacks.update_active_attack()
            
            # drawing
            screen.blit(background.image,(0,0))
            self.game_object.draw(screen)
                 
            pygame.display.flip()               
            clock.tick(60)   
            
        #endwhile
            
            
        
        pygame.quit() 
        
if __name__ == '__main__':
    
    test = TestAttack()
    test.run()
        
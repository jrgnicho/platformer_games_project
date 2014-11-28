#!/usr/bin/env python

import pygame
import rospkg
import sys
from simple_platformer.utilities import *
from simple_platformer.game_object import GameObject
from combat_platformer.attack import Attack

RESOURCE_PACKAGE_NAME =  'simple_platformer'
ANIMATION_SPRITES_PATH = '/resources/hiei_sprites/animation/sprite_list.txt'
COLLISION_SPRITES_PATH = '/resources/hiei_sprites/collision/sprite_list.txt'
SPRITE_KEYS = ['ATTACK_1', 'ATTACK_2', 'ATTACK_3']



class TestAttack(object):
    
    def __init__(self):
        
        self.sprite_loader = SpriteLoader()
        self.game_object = GameObject()
        self.attacks = []
        
    def load_sprites(self):
        
        rospack = rospkg.RosPack()
        coll_file = rospack.get_path(RESOURCE_PACKAGE_NAME) + '/' + COLLISION_SPRITES_PATH
        
        if self.sprite_loader.load_sets(coll_file):
            
            for k in SPRITE_KEYS:
                attack = Attack(self.game_object, self.sprite_loader.sprite_sets[k])
                self.attacks.append(attack)
            
            print "Sprites successfully loaded"
            return True
        else:
            print "Sprites failed to load"
            return False
        
    def run(self):
        
        size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Plausible deniability.")
        
        
        
        if not self.load_sprites():
            pygame.quit() 
            return
        
        pygame.quit() 
        
if __name__ == '__main__':
    
    test = TestAttack()
    test.run()
        
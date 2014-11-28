#!/usr/bin/env python

import pygame
from simple_platformer.utilities import *
import rospkg
import sys


G_Sprite_Loader = SpriteLoader()

def load_sprites():
    
    # checking if file provided in command line
    desc_file = ''
    if len(sys.argv) > 1:
        desc_file = sys.argv[1]
        print "Opening sprite list file %s"%(desc_file)
    else:
        rospack = rospkg.RosPack()
        desc_file = rospack.get_path('simple_platformer') + '/resources/hiei_sprites/animation/sprite_list.txt'
    #endif 
        
    if G_Sprite_Loader.load_sets(desc_file):
        print "Sprites successfully loaded"
        return True
    else:
        print "Sprites failed to load"
        return False
    
    

if __name__ == "__main__":
    
    
    size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Horsy sauce.")
    if not load_sprites():
        exit()
    
    background = pygame.sprite.Sprite()
    background.image = pygame.Surface([ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT])
    background.image.fill(Colors.BLUE)
    background.rect = background.image.get_rect()
    
    sp = pygame.sprite.Sprite()
    sp.image = pygame.Surface([40,60])
    sp.image.fill(Colors.RED)
    sp.rect = sp.image.get_rect()
    sp.rect.centerx = ScreenProperties.SCREEN_WIDTH*0.5
    sp.rect.centery = ScreenProperties.SCREEN_HEIGHT*0.5
    
    # copy of rectange
    rect2 = sp.rect.copy()
    
    active_sprites = pygame.sprite.Group()
    #active_sprites.add(background)
    active_sprites.add(sp)    
    proceed = True
    clock = pygame.time.Clock()
    
    # sprite set keys
    keys = G_Sprite_Loader.sprite_sets.keys()
    
    print "keys in sprite loader %s" % keys
    print "Press N to go to next sprite sequence"
    key_index = 0
    sprite_index = 0
    sprite_set = G_Sprite_Loader.sprite_sets[keys[key_index]]
    time_elapsed = 0
    rate_change = sprite_set.rate_change
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
                
                if event.key == pygame.K_n:
                    key_index += 1
                    
                    # reset if greater that keys available
                    if key_index >= len(keys):
                        key_index = 0                        
                    #endif
                    
                    sprite_set = G_Sprite_Loader.sprite_sets[keys[key_index]]
                    time_elapsed =  pygame.time.get_ticks()
                    sprite_index = 0
                    
                    print "Selected sprite set %s with %i sprites"%(keys[key_index] ,len(sprite_set.sprites))
                    
            #endif
                    
        #endfor
        
        if not proceed:
            break
        #endif
        
        # selecting sprite
        sprite_index = (pygame.time.get_ticks()- time_elapsed)//sprite_set.rate_change        
        if sprite_index >= len(sprite_set.sprites) :
            
            sprite_index = len(sprite_set.sprites) -1  
            sp.image = sprite_set.sprites[sprite_index].image
            time_elapsed =  pygame.time.get_ticks()
            
        else:                           
            sp.image = sprite_set.sprites[sprite_index].image
            
        #endif
        
        # updating rectangle position and size
        
        sp.rect.height = sp.image.get_height()
        sp.rect.bottom = rect2.centery
        
        sp.rect.width = sp.image.get_width()        
        sp.rect.centerx = rect2.centerx
             
        active_sprites.update()
        screen.blit(background.image,(0,0))
        active_sprites.draw(screen)       
 
        
        clock.tick(60)
        
        pygame.display.flip()        
        
    #endwhile
    
    
    pygame.quit() 
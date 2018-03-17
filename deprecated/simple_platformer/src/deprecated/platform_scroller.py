#!/usr/bin/env python

# resources
#http://www.pygame.org/docs/ref/rect.html
#http://programarcadegames.com/python_examples/show_file.php?file=platform_scroller.py

import pygame
from simple_platformer.levels import Level, Platform
from simple_platformer.players import Player
from simple_platformer.utilities import *


            
def main():    
    
    print "Hello mere mortals, prepare to meet your maker"

    # pygame initialization
    pygame.init()
    size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Your wildest dreams will really come true this time.")
    
    # screen bounds
    sb = ScreenBounds()
    
    # create player
    player = Player();    
    player.screen_bounds = sb
    
    # create lever
    platforms = [Platform(100, 200,100, 20),
                 Platform(80, 80,100, 20),
                 Platform(400, 300,100, 20),
                 Platform(450, 20,100, 20),
                 Platform(500, 100,100, 20),
                 Platform(0,-10,1000,20)] # floor
    level1 = Level()
    level1.set_platforms(platforms)
    player.level = level1
    
    # set player start position
    player.rect.x = 300
    player.rect.y = 30
    
    # support objects
    active_sprites = pygame.sprite.Group()
    active_sprites.add(player)
    proceed = True
    clock = pygame.time.Clock()
    
    while proceed:
        
        for event in pygame.event.get():
            
            if event.type  == pygame.QUIT:
                proceed = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move_x(-Player.X_STEP)
                
                if event.key == pygame.K_RIGHT:
                    player.move_x(Player.X_STEP)
                    
                if event.key == pygame.K_ESCAPE:
                    proceed = False
                    break
                    
                if event.key == pygame.K_UP:
                    player.jump()
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.move_x(0)
                    
        #endfor
        
        active_sprites.update()
        level1.update()
        level1.draw(screen)
        active_sprites.draw(screen)
        
        clock.tick(60)
        
        #print "miliseconds elapse " + str(pygame.time.get_ticks())
        
        pygame.display.flip()
        
    #endwhile
    
    pygame.quit()   
        

if __name__ == "__main__":
    
    main()
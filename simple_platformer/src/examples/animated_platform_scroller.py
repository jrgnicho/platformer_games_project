#!/usr/bin/env python

import pygame
from simple_platformer.levels import Level, Platform
from simple_platformer.players import Player
from simple_platformer.players import AnimatedPlayer
from simple_platformer.utilities import *
import rospkg



class PlatformerGame:
    
    def __init__(self):
        
        self.sprite_loader = None
        self.animated_player = None
        self.screen_bounds = None
        self.level = None
        
        
    

    def load_resources(self):
        
        rospack = rospkg.RosPack()
        desc_file = rospack.get_path('simple_platformer') + '/resources/hiei_sprites/sprite_details.txt'
        self.sprite_loader = SpriteLoader()
        if self.sprite_loader.load_sets(desc_file):
            print "Sprites successfully loaded"
            return True
        else:
            print "Sprites failed to load"
            return False
        
        #endif
            
    def setup(self):
        
        if not self.load_resources():
            return False
        #endif
        
        # player setup
        self.screen_bounds = ScreenBounds()
        self.animated_player = AnimatedPlayer()
        self.animated_player.screen_bounds = self.screen_bounds
        
        # set player start position
        self.animated_player.rect.x = 300
        self.animated_player.rect.y = 30
        self.animated_player.rect.width = 35
        self.animated_player.rect.height = 50
        self.animated_player.collision_sprite.rect  = self.animated_player.rect.copy()
        
        # registering resources
        success = True;
        if (self.animated_player.add_animation_sets(AnimatedPlayer.WALK_ACTION,self.sprite_loader.sprite_sets[2],
                                                    self.sprite_loader.sprite_sets[2].invert_set()) and
            
            self.animated_player.add_animation_sets(AnimatedPlayer.STAND_ACTION,self.sprite_loader.sprite_sets[1],
                                                    self.sprite_loader.sprite_sets[1].invert_set()) and
            
            self.animated_player.add_animation_sets(AnimatedPlayer.JUMP_ASCEND_ACTION,self.sprite_loader.sprite_sets[7],
                                                    self.sprite_loader.sprite_sets[7].invert_set()) and
            
            self.animated_player.add_animation_sets(AnimatedPlayer.JUMP_MIDAIR_ACTION,self.sprite_loader.sprite_sets[8],
                                                    self.sprite_loader.sprite_sets[8].invert_set()) and
            
            self.animated_player.add_animation_sets(AnimatedPlayer.JUMP_LAND_ACTION,self.sprite_loader.sprite_sets[9],
                                                    self.sprite_loader.sprite_sets[9].invert_set()) and
            
            self.animated_player.add_animation_sets(AnimatedPlayer.JUMP_ATTACK_ACTION,self.sprite_loader.sprite_sets[10],
                                                    self.sprite_loader.sprite_sets[10].invert_set())) :
            
            print "Added all sprite sets"
        else:
            return False
        
        #endif
        
        # level setup
            # create lever
        platforms = [Platform(100, 200,100, 20),
                     Platform(80, 80,100, 20),
                     Platform(400, 300,100, 20),
                     Platform(450, 20,100, 20),
                     Platform(500, 100,100, 20),
                     Platform(0,-10,1000,20)] # floor
        self.level = Level()
        self.level.set_platforms(platforms)
        self.animated_player.level = self.level
        
        return True
        
    def run(self):
        
        size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("I'm proud of my Papaya fetish.")
        
        if not self.setup():
            print "Setup Failed"
            return False
        

        
        # support objects
        player = self.animated_player
        active_sprites = pygame.sprite.Group()
        active_sprites.add(player)
        proceed = True
        clock = pygame.time.Clock()
        
        while proceed:
            
            #active_sprites.update()
            #self.level.update()
            
            for event in pygame.event.get():
                
                if event.type  == pygame.QUIT:
                    proceed = False
                    break
                
                if event.type == pygame.KEYDOWN:
                    """
                    if event.key == pygame.K_LEFT:
                        player.move_x(-Player.X_STEP)
                    
                    if event.key == pygame.K_RIGHT:
                        player.move_x(Player.X_STEP)
                        
                    """
                        
                    if event.key == pygame.K_ESCAPE:
                        proceed = False
                        break
                        
                    if event.key == pygame.K_UP:
                        player.jump()
                        
                if event.type == pygame.KEYUP:
                    
                    #if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    #    player.move_x(0)
                        
                    if event.key == pygame.K_UP:
                        player.resume_jump()
                        
            #endfor
                        
            # check for pressed keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] :
                player.move_x(-Player.X_STEP)            
                
            if keys[pygame.K_RIGHT]:
                player.move_x(Player.X_STEP)
                        
            if (not keys[pygame.K_LEFT]) and ( not keys[pygame.K_RIGHT]):
                player.move_x(0)
            
            active_sprites.update()
            self.level.update()
            self.level.draw(screen)
            active_sprites.draw(screen)
            
            clock.tick(60)
            
            #print "miliseconds elapse " + str(pygame.time.get_ticks())
            
            pygame.display.flip()
            
        #endwhile
        
if __name__ == "__main__":
    
    # pygame initialization
    pygame.init()
    
    platformer = PlatformerGame()
    platformer.run()
    
    pygame.quit() 
        
        
            
        
        
        
        
        
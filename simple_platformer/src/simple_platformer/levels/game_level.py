import pygame
from simple_platformer.players import AnimatablePlayer
from simple_platformer.players import PlayerStateMachine
from simple_platformer.game_state_machine import ActionKeys
from simple_platformer.utilities import ScreenBounds
from simple_platformer.utilities import Colors, ScreenProperties
from simple_platformer.levels import Platform
from simple_platformer.game_state_machine import *

class GameLevel(pygame.sprite.Sprite,StateMachine):
    
    PLATFORM_CHECK_STEP = 2
    
    def __init__(self,w = ScreenProperties.SCREEN_WIDTH*3,h = ScreenProperties.SCREEN_HEIGHT*4):
        
        pygame.sprite.Sprite.__init__(self)
        StateMachine.__init__(self)
        
        # level objects
        self.player = None # placeholder for PlayerStateMachine object
        self.platforms = pygame.sprite.Group()
        self.enemys  = pygame.sprite.Group()        
        
        # level size
        self.rect = pygame.Rect(0,0,w,h)  
        
        # level screen bounds
        self.screen_bounds = ScreenBounds()
        
    def setup(self):
        
        # setup player
        if self.player == None:
            print "Player has not been added, exiting"
            return False
        else:            
            self.player.collision_sprite.rect.x = 300
            self.player.collision_sprite.rect.y = 30
            
        #endif
        
        
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
        
        self.add_platforms(platforms)
        
        return True
        
    def add_platforms(self,platforms):
        
        # place platforms relative to level
        for p in platforms:
            
            if type(p) is Platform: 
                p.rect.centerx = p.rect.centerx + self.rect.x  
                p.rect.centery = self.rect.centery -  p.rect.y                         
                self.platforms.add(p) 
            #endif                
        #endfor
        
        
    def check_input(self):
        """
            Checks user input and executes the appropriate action
            
            - outputs:    True/False (Quit game)
        """ 
        
        for event in pygame.event.get():
            
            if event.type  == pygame.QUIT:
                #self.player.execute(ActionKeys.EXIT_GAME) 
                return False
            #endif
            
            if event.type == pygame.KEYDOWN:
                    
                if event.key == pygame.K_ESCAPE:
                    #self.player.execute(ActionKeys.EXIT_GAME) 
                    return False
                
                #endif
                
                if event.key == pygame.K_KP0:
                    print "DASH commanded"
                    self.player.execute(ActionKeys.DASH) 
                    
                #endif
                    
                if event.key == pygame.K_UP:                    
                    #print "JUMP commanded"
                    self.player.execute(ActionKeys.JUMP) 
                    
                #endif
                    
            if event.type == pygame.KEYUP:                
                    
                if event.key == pygame.K_UP:
                    self.player.execute(ActionKeys.CANCEL_JUMP) 
                    #print "CANCEL_JUMP commanded"
                    
                #endif
                
                if event.key == pygame.K_KP0:
                    self.player.execute(ActionKeys.CANCEL_DASH) 
                    
                #endif
                
            #endif
                    
        #endfor
                    
        # check for pressed keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] :
            self.player.execute(ActionKeys.MOVE_LEFT)  
        #endif          
            
        if keys[pygame.K_RIGHT]:
            self.player.execute(ActionKeys.MOVE_RIGHT)  
        #endif 
                    
        if (not keys[pygame.K_LEFT]) and ( not keys[pygame.K_RIGHT]):
            self.player.execute(ActionKeys.CANCEL_MOVE)  
        #endif 
            
        return True
        
        
    def update(self):
        """
            Checks user input and steps game.  Also calls the update method on all game objects including the player  
            
            - outputs: True if successful, False otherwise due to game exit condition or user input
        """
        # perform transition or execute action if supported by active state
        self.player.execute(ActionKeys.STEP_GAME)                 
        
        # check user input
        if not self.check_input():
            return False       

        
        # apply gravity
        self.player.execute(ActionKeys.APPLY_GRAVITY)      
        
        # moving and checking collision
        self.player.collision_sprite.rect.centery += self.player.current_upward_speed 
        self.check_collisions_in_y() 
        
        self.player.collision_sprite.rect.centerx += self.player.current_forward_speed 
        self.check_collisions_in_x() 
        
        # check for platform below
        self.check_platform_support()
        
        # check screen and level bounds        
        self.check_level_bounds()
        self.check_screen_bounds()
                   
        # updating objects
        self.enemys.update()  
        self.platforms.update()
        self.player.update()
        
        return True
        
    def draw(self,screen):        
        
        # draw background
        screen.fill(Colors.BLUE)

        # draw objects
        self.platforms.draw(screen)
        self.enemys.draw(screen)
        
        # draw player
        self.player.draw(screen)
        
        
    def scroll(self,dx,dy):
        """ Shifts the world and its objects by incr """
        """ inputs:"""
        """     - incr: Vector2D() value in world coordinates """
        
        self.rect.x += dx
        self.rect.y -= dy
        
        for platform in self.platforms:
            platform.rect.x += dx
            platform.rect.y -= dy
        #endfor
        
        for enemy in self.enemys:
            enemy.rect.x += dx
            enemy.rect.y -= dy
        #endfor  
        
    def check_platform_support(self):
        
        self.player.collision_sprite.rect.y += GameLevel.PLATFORM_CHECK_STEP
        platforms = pygame.sprite.spritecollide(self.player.collision_sprite,self.platforms,False)
        self.player.collision_sprite.rect.y -= GameLevel.PLATFORM_CHECK_STEP
        
        if len(platforms) == 0:
            self.player.execute(ActionKeys.PLATFORM_LOST)
            
        else:
            
            # check if near edge
            for platform in platforms:
                
                # standing on left edge
                distance  = abs(self.player.collision_sprite.rect.right - platform.rect.left)
                w = self.player.collision_sprite.rect.width
                max = w*AnimatablePlayer.STAND_DISTANCE_FROM_EDGE_THRESHOLD
                min = w*AnimatablePlayer.FALL_DISTANCE_FROM_EDGE_THRESHOLD
                
                if distance < max and distance > min:
                    self.player.execute(ActionKeys.LEFT_EDGE_NEAR)
                    #print "Edge distance %f"%(float(distance)/float(w))
                    break
                    
                elif distance <= min :
                    self.player.execute(ActionKeys.PLATFORM_LOST)
                    self.player.collision_sprite.rect.right = platform.rect.left
                    break
                
                #endif
                
                # standing on right edge
                distance = abs(platform.rect.right - self.player.collision_sprite.rect.left )
                if distance < max and distance > min:# and distance < w*AnimatablePlayer.FALL_DISTANCE_FROM_EDGE_THRESHOLD:
                    self.player.execute(ActionKeys.RIGHT_EDGE_NEAR)
                    #print "Edge distance %f"%(float(distance)/float(w))
                    break
                    
                elif distance <= min:
                    self.player.execute(ActionKeys.PLATFORM_LOST)
                    self.player.collision_sprite.rect.left = platform.rect.right
                    
                    break
                
                #endif
                
          #endif  
            
        
    def check_collisions_in_y(self):        
     
        
        # find colliding platforms in the y direction         
        platforms = pygame.sprite.spritecollide(self.player.collision_sprite,self.platforms,False)     
        for platform in platforms:
            
            if self.player.collision_sprite.rect.centery < platform.rect.centery:
                self.player.collision_sprite.rect.bottom = platform.rect.top
                self.player.execute(ActionKeys.COLLISION_BELOW,[platform.rect.top])  
                              
            #elif self.player.collision_sprite.rect.top < platform.rect.bottom :
            else:
                self.player.collision_sprite.rect.top = platform.rect.bottom
                self.player.execute(ActionKeys.COLLISION_ABOVE,[platform.rect.bottom])
            #endif
        
        #endfor               
                
    def check_collisions_in_x(self): 
            
                
        # find colliding platforms in the x direction            
        platforms = pygame.sprite.spritecollide(self.player.collision_sprite,self.platforms,False)     
        for platform in platforms:
            
            if self.player.collision_sprite.rect.centerx > platform.rect.centerx:
                self.player.collision_sprite.rect.left = platform.rect.right
                #self.player.execute(ActionKeys.RECTIFY_LEFT,[platform.rect.right])
                
            #elif self.player.collision_sprite.rect.right > platform.rect.left:
            else:
                self.player.collision_sprite.rect.right = platform.rect.left
                #self.player.execute(ActionKeys.RECTIFY_RIGHT,[platform.rect.left])
                
            #endif          
            
        #endfor 
        
         
        
    def check_screen_bounds(self):
        
        scroll_x = 0
        scroll_y = 0
        
        # vertical bounds
        if self.player.collision_sprite.rect.bottom > self.screen_bounds.rect.bottom : # below ground level
            scroll_y = -(self.screen_bounds.rect.bottom - self.player.collision_sprite.rect.bottom)
            self.player.collision_sprite.rect.bottom = self.screen_bounds.rect.bottom 
            
        elif self.player.collision_sprite.rect.top < self.screen_bounds.rect.top: # above level top
            scroll_y = -(self.screen_bounds.rect.top - self.player.collision_sprite.rect.top)
            self.player.collision_sprite.rect.top = self.screen_bounds.rect.top
            
        # horizontal bounds
        if self.player.collision_sprite.rect.right > self.screen_bounds.rect.right : # too far to the right
            scroll_x = self.screen_bounds.rect.right - self.player.collision_sprite.rect.right
            self.player.collision_sprite.rect.right = self.screen_bounds.rect.right 
            #print "Scrolling right, screen right bound of %d exceeded"%self.screen_bounds.rect.right
            
        elif self.player.collision_sprite.rect.left < self.screen_bounds.rect.left: # too far to the left
            scroll_x = self.screen_bounds.rect.left - self.player.collision_sprite.rect.left
            self.player.collision_sprite.rect.left = self.screen_bounds.rect.left
            #print "Scrolling left"
            
        # scrolling level 
        self.scroll(scroll_x,scroll_y)
        
    def check_level_bounds(self):
        
        # vertical bounds
        if self.player.collision_sprite.rect.bottom > self.rect.bottom : # below ground level
            self.player.collision_sprite.rect.bottom = self.rect.bottom
            
        elif self.player.collision_sprite.rect.top < self.rect.top: # above level top
            self.player.collision_sprite.rect.top = self.rect.top
        
        #endif        
         
        # horizontal bounds
        if self.player.collision_sprite.rect.right  > self.rect.right:
            self.player.collision_sprite.rect.right = self.rect.right
            
        elif self.player.collision_sprite.rect.left < self.rect.left:
            self.player.collision_sprite.rect.left = self.rect.left
            
        #endif
            
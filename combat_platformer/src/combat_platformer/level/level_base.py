import pygame
from simple_platformer.utilities import GameProperties
from simple_platformer.utilities import ScreenBounds
from simple_platformer.utilities import Colors, ScreenProperties
from simple_platformer.levels import Platform
from simple_platformer.game_state_machine import *
from combat_platformer.player.action_keys import *
from combat_platformer.player import PlayerBase
from combat_platformer.player import PlayerStateMachine


class LevelBase(pygame.sprite.Sprite):
    
    PLATFORM_CHECK_STEP = 2
    
    def __init__(self,w = ScreenProperties.SCREEN_WIDTH*3,h = ScreenProperties.SCREEN_HEIGHT*4):
        
        pygame.sprite.Sprite.__init__(self)
        
        # level objects
        self.player = None # placeholder for PlayerStateMachine object
        self.platforms = pygame.sprite.Group()
        self.enemys  = pygame.sprite.Group()        
        
        # level size
        self.rect = pygame.Rect(0,0,w,h)  
        
        # level screen bounds
        self.screen_bounds = ScreenBounds()
        
        # background
        self.background = None
        
    def load_background(self,file_name):
        
        self.background = pygame.image.load(file_name).convert()
        self.background.set_colorkey(Colors.WHITE)  
        self.background = self.scale_background(self.background) 
        background_rect = self.background.get_rect().copy()    
        
        # background scrolling members
        Gx = 0.5 * (ScreenProperties.SCREEN_WIDTH - self.screen_bounds.rect.width)  
        Gy = 0.5 * (ScreenProperties.SCREEN_HEIGHT - self.screen_bounds.rect.height)
        
        # change ratio in x
        dx = float(background_rect.width - ScreenProperties.SCREEN_WIDTH)/float(self.rect.width - self.screen_bounds.rect.width)
        
        # change ratio in y
        dy = float(background_rect.height - ScreenProperties.SCREEN_HEIGHT)/float(self.rect.height - self.screen_bounds.rect.height)
        
        # creating interpolation function for computing background position as a function of level position
        self.interp_background_position = lambda lx,ly : (float(lx - Gx)*dx,float(ly- Gy)*dy)      

        
        return True
    
    def scale_background(self,img):
        """
        Scales the background image so that its size is between that of the screen and the level 
        where screen < background < level       
        
        """
        rect = img.get_rect().copy()
        sx = 1
        sy = 1
        s = 1
        w = rect.width
        h = rect.height
        if rect.width < ScreenProperties.SCREEN_WIDTH:
            
            sx = 0.6*float(self.rect.width)/float(w)            
        #endif
        
        if rect.height < ScreenProperties.SCREEN_HEIGHT:
            
            sy = 0.6*float(self.rect.height)/float(h)
        #endif
            
        # use largest scale    
        if sx > sy:            
            s = sx
            
        else:            
            s = sy
            
        #endif
        
        scaled_image = img
        if s != 1:
            w = int(s*w)
            h = int(s*h)
            
            scaled_image = pygame.transform.smoothscale(img,(w,h))                    
            print "Scaled background from size %i x %i to %i x %i"%(rect.width,rect.height,w,h)
            
        else:
            print "Using default background size of %i x %i"%(rect.width,rect.height)
        
        #endif
        
        return scaled_image    
        
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
                     Platform(800,110,600,20),
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
                return False
            #endif
            
            if event.type == pygame.KEYDOWN:
                    
                if event.key == pygame.K_ESCAPE:
                    return False
                
                #endif
                
                if event.key == pygame.K_z:
                    self.player.execute(PlayerActionKeys.DASH) 
                    
                #endif
                
                if event.key == pygame.K_UP:
                    self.player.execute(PlayerActionKeys.MOVE_UP) 
                    
                #endif
                    
                if event.key == pygame.K_x:                    
                    #print "JUMP commanded"
                    self.player.execute(PlayerActionKeys.JUMP) 
                    
                #endif
                    
            if event.type == pygame.KEYUP:                
                    
                if event.key == pygame.K_x: #K_UP:
                    self.player.execute(PlayerActionKeys.CANCEL_JUMP) 
                    #print "CANCEL_JUMP commanded"
                    
                #endif
                
                if event.key == pygame.K_z: #K_KP0:
                    self.player.execute(PlayerActionKeys.CANCEL_DASH) 
                    
                #endif
                
            #endif
                    
        #endfor
                    
        # check for pressed keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] :
            self.player.execute(PlayerActionKeys.MOVE_LEFT)  
        #endif          
            
        if keys[pygame.K_RIGHT]:
            self.player.execute(PlayerActionKeys.MOVE_RIGHT)  
        #endif 
                    
        if (not keys[pygame.K_LEFT]) and ( not keys[pygame.K_RIGHT]):
            self.player.execute(PlayerActionKeys.CANCEL_MOVE)  
        #endif 
            
        return True
        
        
    def update(self):
        """
            Checks user input and steps game.  Also calls the update method on all game objects including the player  
            
            - outputs: True if successful, False otherwise due to game exit condition or user input
        """
        # perform transition or execute action if supported by active state
        self.player.execute(PlayerActionKeys.STEP_GAME)                 
        
        # check user input
        if not self.check_input():
            return False       

        
        # apply gravity
        self.player.execute(PlayerActionKeys.APPLY_GRAVITY,[GameProperties.GRAVITY_ACCELERATION])   
        
        # moving and checking collision           
        self.player.update_pos_x()
        self.check_collisions_in_x()         
            
        self.player.update_pos_y()
        self.check_collisions_in_y() 
        
        
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
        if self.background != None:
            
            (x,y) = self.interp_background_position(self.rect.x,self.rect.y)
            screen.blit(self.background,(int(x),int(y)))
            

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
        
        self.player.collision_sprite.rect.y += LevelBase.PLATFORM_CHECK_STEP
        platforms = pygame.sprite.spritecollide(self.player.collision_sprite,self.platforms,False)
        self.player.collision_sprite.rect.y -= LevelBase.PLATFORM_CHECK_STEP
        
        ps = self.player.collision_sprite
        if len(platforms) == 0:
            self.player.execute(PlayerActionKeys.PLATFORM_LOST)                   
        #endif  
            
        
    def check_collisions_in_y(self):        
     
        
        # find colliding platforms in the y direction         
        platforms = pygame.sprite.spritecollide(self.player.collision_sprite,self.platforms,False)   

        for platform in platforms:
            
            if self.player.collision_sprite.rect.centery < platform.rect.centery:
                self.player.collision_sprite.rect.bottom = platform.rect.top
                self.player.execute(PlayerActionKeys.COLLISION_BELOW,[platform])  
                              
            else:
                self.player.collision_sprite.rect.top = platform.rect.bottom
                self.player.execute(PlayerActionKeys.COLLISION_ABOVE,[platform])
            #endif
    
        #endfor    
        
        # checking range collision sprites
        pr = self.player.collision_sprite.rect
        for rs in iter(self.player.range_collision_group):
            rs.rect.center = pr.center
            platforms = pygame.sprite.spritecollide(rs,self.platforms,False)
            if len(platforms) > 0:
                self.player.execute(PlayerActionKeys.PLATFORMS_IN_RANGE,[platforms])   

                
                
    def check_collisions_in_x(self): 
            
                
        # find colliding platforms in the x direction            
        platforms = pygame.sprite.spritecollide(self.player.collision_sprite,self.platforms,False)     
        for platform in platforms:
            
            if self.player.collision_sprite.rect.centerx > platform.rect.centerx:
                self.player.collision_sprite.rect.left = platform.rect.right
                self.player.execute(PlayerActionKeys.COLLISION_LEFT_WALL,[platform])
                
            else:
                self.player.collision_sprite.rect.right = platform.rect.left
                self.player.execute(PlayerActionKeys.COLLISION_RIGHT_WALL,[platform])
                
            #endif          
            
        #endfor 
        
        # checking range collision sprites
        pr = self.player.collision_sprite.rect
        for rs in iter(self.player.range_collision_group):
            rs.rect.center = pr.center
            platforms = pygame.sprite.spritecollide(rs,self.platforms,False)
            if len(platforms) > 0:
                self.player.execute(PlayerActionKeys.PLATFORMS_IN_RANGE,[platforms])
                
        
         
        
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
            
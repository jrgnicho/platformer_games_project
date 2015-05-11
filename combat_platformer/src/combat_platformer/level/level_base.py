import pygame
from simple_platformer.utilities import GameProperties
from simple_platformer.utilities import ScreenBounds
from simple_platformer.utilities import Colors, ScreenProperties
from simple_platformer.game_state_machine import StateMachine
from simple_platformer.game_object import GameObject
from simple_platformer.game_state_machine import *
from combat_platformer.level import Platform
from combat_platformer.level.action_keys import *
from combat_platformer.player.action_keys import *
from combat_platformer.player import PlayerBase
from combat_platformer.enemy import EnemyBase
from simple_platformer.game_object.animatable_object import AnimatableObject


class LevelBase(GameObject):
    
    PLATFORM_CHECK_STEP = 2
    
    def __init__(self,w = ScreenProperties.SCREEN_WIDTH*4,h = ScreenProperties.SCREEN_HEIGHT*4):
        
        GameObject.__init__(self,0,0,w,h)
        
        # level objects
        self.__player__ = None # placeholder for PlayerStateMachine object
        self.__platforms__ = pygame.sprite.Group()
        self.__enemies_group__ = pygame.sprite.Group() 
                
        # level screen bounds
        self.screen_bounds = ScreenBounds()
        
        # background
        self.background = None
        
        # collision detection
        self.__game_objects__ = pygame.sprite.Group()        
        
        # drawing
        self.__screen_objects__ = pygame.sprite.OrderedUpdates() # will be updated to hold all objects in the screen
        self.__screen_region__ = pygame.sprite.Sprite()
        self.__screen_region__.rect = self.screen_bounds.rect.copy()
        self.__screen_region__.rect.size = (ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT)
                
        # input
        self.__input_events__ = (pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP)
        
        # 
    
    @property
    def player(self):
        return self.__player__
    
    @player.setter    
    def player(self,player):
        self.__player__ = player
        self.__player__.parent_object = self
        
        self.__game_objects__.add(player)
        
        
    def add_enemy(self,enemy):
        enemy.parent_object = self
        self.__enemies_group__.add(enemy)
        
        self.__game_objects__.add(enemy)
        
    def select_screen_objects(self):
        
        # set coordinates for screen region
        self.__screen_objects__.empty()
        self.__screen_region__.rect.top = -self.rect.top
        self.__screen_region__.rect.left = -self.rect.left
                  
        # find platforms on screen
        self.__screen_objects__.add(pygame.sprite.spritecollide(self.__screen_region__,
                                                                 self.__platforms__,
                                                                  False, None))        
        # find enemies on screen
        self.__screen_objects__.add(pygame.sprite.spritecollide(self.__screen_region__,
                                                                 self.__enemies_group__,
                                                                  False, None))
        # add player last
        self.__screen_objects__.add(self.__player__)
   
    def load_background(self,file_name):
        
        self.background = pygame.image.load(file_name).convert()
        #self.background.set_colorkey(Colors.WHITE)  
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
        
        # event setup (must be done here once the display has been initialized)
        pygame.event.set_allowed(None)
        pygame.event.set_allowed(self.__input_events__)
        pygame.event.set_allowed(AnimatableObject.Events.EVENTS_LIST)
        pygame.event.set_allowed(StateMachine.Events.EVENTS_LIST)
        
        # setup player
        if self.__player__ == None:
            print "Player has not been added, exiting"
            return False            
        #endif
        
        
        # create lever
        platforms = [Platform(500, 1220,200, 20),
                     Platform(400 , 1100,100, 20),
                     Platform(200, 1160,100, 20),
                     Platform(10, 1500,100, 20),
                     Platform(400, 1450,100, 20),
                     Platform(600, 1400,520, 20),
                     Platform(950, 1000,220, 20),
                     Platform(200, 1700,460, 20),
                     Platform(800, 1800,100, 20),
                     Platform(500,1920,600,20),
                     Platform(1700, 1600,800, 20),
                     Platform(2050, 1800,200, 20),
                     Platform(1400,1400,200,20),
                     Platform(1600,1900,100,20),
                     Platform(1560,1700,200,20),
                     Platform(1300,1300,200,20),
                     Platform(1800,1200,100,20),
                     Platform(3600,1940,100,180),
                     Platform(-20,10,40,2090),
                     Platform(2200,1940,40,160),                     
                     Platform(-500, 2100,4100,20)]  
        
        self.add_platforms(platforms)
        
        return True
        
    def add_platforms(self,platforms):
        
        # place platforms relative to level
        for p in platforms:
            
            if type(p) is Platform: 
                p.parent_object = self                      
                self.__platforms__.add(p) 
            #endif                
        #endfor
        
    def process_animation_events(self):
        
        for event in pygame.event.get(AnimatableObject.Events.EVENTS_LIST):
            event.notify()
        #endif
        
    def process_state_machine_events(self):
        
        for event in pygame.event.get(StateMachine.Events.EVENTS_LIST):
            event.notify()
        #endif
        
        
    def process_input_events(self):
        """
            Checks user input and executes the appropriate action
            
            - outputs:    True/False (Quit game)
        """ 
        
        for event in pygame.event.get(self.__input_events__):
            
            if event.type  == pygame.QUIT:
                return False
            #endif
            
            if event.type == pygame.KEYDOWN:
                    
                if event.key == pygame.K_ESCAPE:
                    return False
                
                #endif
                
                if event.key == pygame.K_z:
                    self.__player__.execute(PlayerActionKeys.DASH) 
                    
                #endif
                
                if event.key == pygame.K_s:
                    self.__player__.execute(PlayerActionKeys.ATTACK) 
                #endif
                
                if event.key == pygame.K_UP:
                    self.__player__.execute(PlayerActionKeys.MOVE_UP) 
                    
                #endif
                    
                if event.key == pygame.K_x:                    
                    #print "JUMP commanded"
                    self.__player__.execute(PlayerActionKeys.JUMP) 
                    
                #endif
                    
            if event.type == pygame.KEYUP:                
                    
                if event.key == pygame.K_x: #K_UP:
                    self.__player__.execute(PlayerActionKeys.CANCEL_JUMP) 
                    #print "CANCEL_JUMP commanded"
                    
                #endif
                
                if event.key == pygame.K_z: #K_KP0:
                    self.__player__.execute(PlayerActionKeys.CANCEL_DASH) 
                    
                #endif
                
            #endif
                    
        #endfor
                    
        # check for pressed keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] :
            self.__player__.execute(PlayerActionKeys.MOVE_LEFT)  
        #endif          
            
        if keys[pygame.K_RIGHT]:
            self.__player__.execute(PlayerActionKeys.MOVE_RIGHT)  
        #endif 
                    
        if (not keys[pygame.K_LEFT]) and ( not keys[pygame.K_RIGHT]):
            self.__player__.execute(PlayerActionKeys.CANCEL_MOVE)  
        #endif 
            
        return True
        
        
    def update(self,elapsed_time):
        """
            Checks user input and steps game.  Also calls the update method on all game objects including the player  
            
            - outputs: True if successful, False otherwise due to game exit condition or user input
        """     

        # check user input
        if not self.process_input_events():
            return False 
        #endif
        
        # common game actions
        for game_object in self.__game_objects__:    
            # step game object
            game_object.execute(LevelActionKeys.STEP_GAME,[elapsed_time])
            # apply gravity
            game_object.execute(LevelActionKeys.APPLY_GRAVITY,[GameProperties.GRAVITY_ACCELERATION])
        #endfor
        
        self.process_state_machine_events()
        
        # process all game objects interactions with the level objects and rules (enemies, player, etc)
        self.process_game_collisions(elapsed_time)
            
        # checks player position on the screen in order to scroll the level
        self.process_screen_bounds()
                
        # update all objects
        self.__platforms__.update()
        self.__game_objects__.update()        
        
        return True
    
    def process_game_collisions(self,elapsed_time): 
        
        game_objects = pygame.sprite.Group()
        collision_group = pygame.sprite.Group() 
        for game_object in self.__game_objects__:       
        
            # step game object
            #game_object.execute(LevelActionKeys.STEP_GAME,[elapsed_time])
            
            # apply gravity
            #game_object.execute(LevelActionKeys.APPLY_GRAVITY,[GameProperties.GRAVITY_ACCELERATION])
            
            game_objects.empty()
            game_objects.add(self.__game_objects__.sprites())
            game_objects.remove(game_object)
            
            # check bitmasks  
            collision_group.empty()    
            for obj in iter(game_objects):
               if any(game_object.collision_bitmask & obj.type_bitmask):
                    collision_group.add(obj)
                #endif  
            
            # checking collisions in the x direction
            game_object.step_x()
            self.process_level_x_collisions(game_object)
            self.process_objects_x_collisions(game_object, collision_group)
            
            # checking collisions in the y direction
            game_object.step_y()
            self.process_level_y_collisions(game_object)
            self.process_objects_y_collisions(game_object, collision_group)      
    
            # check range collision sprites against platforms
            range_sprites = game_object.range_collision_group
            for rs in iter(range_sprites):
                                        
                if pygame.sprite.spritecollideany(rs, self.__platforms__, None):            
                    platforms = pygame.sprite.spritecollide(rs,self.__platforms__,False)
                    game_object.execute(LevelActionKeys.PLATFORMS_IN_RANGE,[platforms]) 
                #endif
            #endfor
            
            # check range collisions against other objects
            for obj in iter(collision_group):
                
                if pygame.sprite.spritecollideany(obj,range_sprites, None):            
                    collided = pygame.sprite.spritecollide(obj,range_sprites, False)
                    game_object.execute(LevelActionKeys.GAME_OBJECT_IN_RANGE,[obj,collided])
                #endif
            #endfor     
            
            # check for platform collisions
            self.process_platform_support(game_object)
            
            # check screen and level bounds        
            self.process_level_bounds(game_object)       

        
    def process_objects_x_collisions(self,game_object,game_objects):   
            
        # check collisions
        if pygame.sprite.spritecollideany(game_object, game_objects):   
            
            # check collisions
            collided = pygame.sprite.spritecollide(game_object, game_objects,False, None)
            for col_obj in collided:
                if game_object.rect.centerx > col_obj.rect.centerx:
                    game_object.execute(LevelActionKeys.GAME_OBJECT_COLLISION_LEFT,[col_obj])                
                else:
                    game_object.execute(LevelActionKeys.GAME_OBJECT_COLLISION_RIGHT,[col_obj])                
                #endif 
            #endfor
            
        #endif
            
    def process_objects_y_collisions(self,game_object,game_objects):   

        # check collisions
        if pygame.sprite.spritecollideany(game_object, game_objects):               
            # check collisions
            collided = pygame.sprite.spritecollide(game_object, game_objects,False, None)
            for col_obj in collided:
                
                if game_object.rect.centery < col_obj.rect.centery:
                    game_object.execute(LevelActionKeys.GAME_OBJECT_COLLISION_BELOW,[col_obj])                
                else:
                    game_object.execute(LevelActionKeys.GAME_OBJECT_COLLISION_ABOVE,[col_obj])                
                #endif 
            #endfor     
                   
        #endif
        
    def draw(self,screen):        
        
        # draw background        
        screen.fill(Colors.BLUE)
        if self.background != None:
            
            (x,y) = self.interp_background_position(self.rect.x,self.rect.y)
            screen.blit(self.background,(int(x),int(y)))
        #endif    


        # selecting objects in screen for drawing
        self.select_screen_objects()  
        for game_object in iter(self.__screen_objects__):
            game_object.draw(screen)
        #endfor 
        
        self.process_animation_events()    
        
        
    def scroll(self,dx,dy):
        """ Shifts the world and its objects by (dx,dy)"""
                
        self.rect.x += dx
        self.rect.y += dy        
        
    def process_platform_support(self,game_object):
        
        game_object.rect.y += LevelBase.PLATFORM_CHECK_STEP
        platform_found = pygame.sprite.spritecollideany(game_object,self.__platforms__)
        game_object.rect.y -= LevelBase.PLATFORM_CHECK_STEP
        
        if not platform_found:
            game_object.execute(LevelActionKeys.PLATFORM_SUPPORT_LOST)                   
        else:
            game_object.rect.y += LevelBase.PLATFORM_CHECK_STEP
            platforms = pygame.sprite.spritecollide(game_object,self.__platforms__,False)
            game_object.rect.y -= LevelBase.PLATFORM_CHECK_STEP
            for p in platforms:
                cx = game_object.rect.centerx
                if (cx > p.rect.right) and ((cx - p.rect.right) > game_object.properties.distance_from_platform_edge):
                    game_object.rect.left = p.rect.right
                    game_object.execute(LevelActionKeys.PLATFORM_SUPPORT_LOST)
                    break
                elif cx < p.rect.left and ((p.rect.left - cx) > game_object.properties.distance_from_platform_edge ):
                    game_object.rect.right = p.rect.left
                    game_object.execute(LevelActionKeys.PLATFORM_SUPPORT_LOST)
                    break
                #endif
            #endfor
            
    def process_level_y_collisions(self,game_object):     
        
        if pygame.sprite.spritecollideany(game_object, self.__platforms__, None):
            # find colliding platforms in the y direction         
            platforms = pygame.sprite.spritecollide(game_object,self.__platforms__,False)   
    
            for platform in platforms:
                
                if game_object.rect.centery < platform.rect.centery:
                    game_object.rect.bottom = platform.rect.top
                    game_object.execute(LevelActionKeys.PLATFORM_COLLISION_BELOW,[platform])  
                                  
                else:
                    game_object.rect.top = platform.rect.bottom
                    game_object.execute(LevelActionKeys.PLATFORM_COLLISION_ABOVE,[platform])
                #endif        
            #endfor                
        #endif
           
    def process_level_x_collisions(self,game_object):             
              
        if pygame.sprite.spritecollideany(game_object, self.__platforms__, None):  
            # find colliding platforms in the x direction            
            platforms = pygame.sprite.spritecollide(game_object,self.__platforms__,False)     
            for platform in platforms:
                
                if game_object.rect.centerx > platform.rect.centerx:
                    game_object.rect.left = platform.rect.right
                    game_object.execute(LevelActionKeys.PLATFORM_COLLISION_LEFT,[platform])
                    
                else:
                    game_object.rect.right = platform.rect.left
                    game_object.execute(LevelActionKeys.PLATFORM_COLLISION_RIGHT,[platform])                
                #endif        
            #endfor 
        #endif
        
    def process_screen_bounds(self):
        
        scroll_x = 0
        scroll_y = 0
        
        # vertical bounds
        if self.__player__.screen_bottom > self.screen_bounds.rect.bottom : # below ground level
            scroll_y = (self.screen_bounds.rect.bottom - self.__player__.screen_bottom)
            
        elif self.__player__.screen_top < self.screen_bounds.rect.top: # above level top
            scroll_y = (self.screen_bounds.rect.top - self.__player__.screen_top)
        #endif
            
        # horizontal bounds
        if self.__player__.screen_right > self.screen_bounds.rect.right : # too far to the right
            scroll_x = self.screen_bounds.rect.right - self.__player__.screen_right     
                   
        elif self.__player__.screen_left < self.screen_bounds.rect.left: # too far to the left
            scroll_x = self.screen_bounds.rect.left - self.__player__.screen_left
        #endif
            
        # scrolling level 
        self.scroll(scroll_x,scroll_y)
        
    def process_level_bounds(self,game_object):
        
        # vertical bounds
        if game_object.rect.bottom > self.rect.height : # below ground level
            game_object.rect.bottom = self.rect.height
            
        elif game_object.rect.top < 0: # above level top
            game_object.rect.top = 0        
        #endif        
         
        # horizontal bounds
        if game_object.rect.right  > self.rect.width:
            game_object.rect.right = self.rect.width
            
        elif game_object.rect.left < 0:
            game_object.rect.left = 0            
        #endif
            
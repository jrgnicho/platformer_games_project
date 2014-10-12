import pygame
from simple_platformer.game_state_machine import State
from combat_platformer.level.action_keys import LevelActionKeys
from combat_platformer.player.action_keys import PlayerActionKeys



class StateKeys(object):
    
        NONE=""
        STANDING="STANDING"
        STANDING_ON_EDGE="STANDING_ON_EDGE"
        RUNNING="RUNNING"
        JUMPING="JUMPING"
        FALLING="FALLING"
        LANDING="LANDING"
        DASHING= "DASHING"
        DASH_BREAKING= "DASH_BREAKING"
        MIDAIR_DASHING = "MIDAIR_DASHING"
        HANGING = "HANGING"
        CLIMBING = "CLIMBING"
        EXIT = "EXIT"

class BasicState(State):
    
    
    def __init__(self,key,player):
        
        print "State key " + key
        State.__init__(self,key)
        self.player = player
    
    """
    This method shall be implemented by all subclasses in order to load the corresponding game assets for that state
    """   
    def setup(self,asset):
        print "setup(...) method for state %s unimplemented"%(self.key)
    
    
class RunState(BasicState):

    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.RUNNING,player)        
    
        
        self.speed = self.player.properties.run_speed
        
        self.add_action(PlayerActionKeys.MOVE_LEFT,lambda : self.player.turn_left(-self.speed))
        self.add_action(PlayerActionKeys.MOVE_RIGHT,lambda : self.player.turn_right(self.speed))
        self.add_action(LevelActionKeys.STEP_GAME,lambda time_elapsed :self.player.step_momentum())
        
    
    def enter(self):
        
        self.player.max_delta_x = self.speed            
        self.player.set_current_animation_key(StateKeys.RUNNING),
        self.player.set_horizontal_speed(self.speed)  
        
    def exit(self):
        self.player.max_delta_x = self.player.properties.dash_speed  
        
        
class DashState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.DASHING,player)
        
    def setup(self,asset):     
                
        pass
        
    def enter(self):
        
       # perform dash
       self.player.set_current_animation_key(StateKeys.DASHING),
       self.player.set_horizontal_speed(self.player.properties.dash_speed)
       
    
    def exit(self):
        
        progress_percent = self.player.get_animation_progress_percentage()
        self.player.set_momentum(0.8*self.player.properties.dash_speed 
                                                      if progress_percent>0.3 else 0)

        
        
        
class MidairDashState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.MIDAIR_DASHING,player)
    
        
        
    def setup(self,asset):       
                
        # creating collision rectangle
        pass
        
        
    def midair_dash(self):
        
        plyr = self.player
        plyr.set_current_animation_key(StateKeys.MIDAIR_DASHING),
        plyr.set_horizontal_speed(self.player.properties.dash_speed)
        plyr.set_vertical_speed(0)
        plyr.midair_dash_countdown -=1
        
        
    def enter(self):
                
        self.midair_dash()
        
    def exit(self):
        
        plyr = self.player
        plyr.set_momentum(plyr.properties.dash_speed * plyr.get_animation_progress_percentage())     
        
        
class DashBreakingState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self, StateKeys.DASH_BREAKING, player)
        
        self.add_action(PlayerActionKeys.ACTION_SEQUENCE_EXPIRED,
                            lambda : self.player.set_current_animation_key(StateKeys.DASH_BREAKING,[-1])) 
        self.add_action(LevelActionKeys.STEP_GAME,lambda time_elapsed :self.update())
        
    def enter(self):
        
        plyr = self.player
        plyr.set_momentum(plyr.properties.run_speed)
        plyr.set_horizontal_speed(0),
        plyr.set_current_animation_key(StateKeys.DASH_BREAKING)
    
    def update(self):
        self.player.step_momentum()
        self.player.set_horizontal_speed(abs(self.player.momentum))
          
        
    def exit(self):
        
        self.player.set_momentum(0)


    
class StandState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.STANDING,player)
        self.is_standing_on_edge = False
        self.is_beyond_edge = False     

        
        self.add_action(LevelActionKeys.PLATFORMS_IN_RANGE,lambda platforms: self.check_near_edge(platforms)) 
        
    def setup(self,asset):
        
        # creating range rectangle
        self.range_height_extension = 4
        self.range_sprite = pygame.sprite.Sprite()
        self.range_sprite.rect = self.player.rect.copy()
        self.range_sprite.rect.height = self.range_sprite.rect.height + self.range_height_extension

        
        
    def enter(self):
        
        self.player.set_horizontal_speed(0)
        self.player.set_current_animation_key(StateKeys.STANDING)
        self.player.set_momentum(0)
        self.player.midair_dash_countdown = self.player.properties.max_midair_dashes
        self.player.range_collision_group.add(self.range_sprite) 
        self.is_standing_on_edge = False
        self.is_beyond_edge = False
        
        
    def exit(self):
        
        self.player.range_collision_group.remove(self.range_sprite) 
        
    def check_near_edge(self,platforms):
        
                    
        # check if near edge
        ps = self.player
        for platform in platforms:
            
            if platform.rect.top < ps.rect.top:
                continue
            #endif                    
            
            w = ps.rect.width
            max = w*self.player.properties.max_distance_from_edge
            min = w*self.player.properties.min_distance_from_edge
            
            # finding side of platform
            on_platform_right = ps.rect.centerx > platform.rect.centerx
            
            # standing on left edge
            distance  = abs(platform.rect.right - ps.rect.left ) \
            if on_platform_right else abs(ps.rect.right - platform.rect.left)

            
            if distance < max and distance > min:
                self.is_standing_on_edge = (on_platform_right == self.player.facing_right)
                break
                
            elif distance <= min :                        
                self.is_beyond_edge = True
                
                if on_platform_right:
                    ps.rect.left = platform.rect.right
                else:
                    ps.rect.right = platform.rect.left
                    
                #endif    
                    
                break                    
            
            #endif
            
        #endfor          
        
        
class StandOnEdgeState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.STANDING_ON_EDGE,player)
        
        move_speed = self.player.properties.run_speed
        self.add_action(PlayerActionKeys.MOVE_LEFT,lambda : self.player.turn_left(-move_speed))
        self.add_action(PlayerActionKeys.MOVE_RIGHT,lambda : self.player.turn_right(move_speed))
        self.add_action(PlayerActionKeys.ACTION_SEQUENCE_EXPIRED,lambda : self.player.set_current_animation_key(StateKeys.STANDING_ON_EDGE,[-1]))
        
    def enter(self):
        
        plyr = self.player
        plyr.set_current_animation_key(StateKeys.STANDING_ON_EDGE)
        plyr.set_horizontal_speed(0)
        
        
class JumpState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.JUMPING,player)
        
        self.speed = 0
        
        self.has_landed = False
        self.edge_in_reach = False                   
        self.hang_sprite = pygame.sprite.Sprite()

        
        self.add_action(PlayerActionKeys.MOVE_LEFT,lambda : self.turn_left())
        self.add_action(PlayerActionKeys.MOVE_RIGHT,lambda : self.turn_right())                
        self.add_action(PlayerActionKeys.CANCEL_MOVE,lambda : self.cancel_move())
        self.add_action(PlayerActionKeys.CANCEL_JUMP,lambda : self.cancel_jump())
        self.add_action(LevelActionKeys.APPLY_GRAVITY,lambda g: self.player.apply_gravity(g))    
        self.add_action(LevelActionKeys.COLLISION_ABOVE,lambda platform : self.player.set_vertical_speed(0))
        self.add_action(LevelActionKeys.COLLISION_BELOW,self.check_landing)
        self.add_action(LevelActionKeys.COLLISION_RIGHT_WALL,lambda platform : self.player.set_momentum(0))
        self.add_action(LevelActionKeys.COLLISION_LEFT_WALL,lambda platform : self.player.set_momentum(0)) 
        self.add_action(LevelActionKeys.PLATFORMS_IN_RANGE,lambda platforms: self.check_near_edge(platforms))  
        
    def setup(self,asset):
        
        self.hang_sprite.rect =  pygame.Rect(0,0,2*self.player.properties.hang_radius,
                                                 2*self.player.properties.hang_radius) 
        
        self.speed = self.player.properties.run_speed
        
        # creating range rectangle
        self.range_sprite = pygame.sprite.Sprite()
        self.range_sprite.rect = self.player.rect.copy()
        self.range_sprite.rect.width = self.range_sprite.rect.width + self.hang_sprite.rect.width
        self.range_sprite.rect.height = self.range_sprite.rect.height + self.hang_sprite.rect.height
        
    def turn_right(self):
        
        pl = self.player
        if pl.momentum >0:
        
            pl.turn_right(pl.momentum if pl.momentum > self.speed else self.speed)
        else:
            pl.turn_right(self.speed + pl.momentum)                
            pl.step_momentum()
                
            #endif
        #endif
            
        
    def turn_left(self):
        
        pl = self.player
        if pl.momentum <0:
        
            pl.turn_left(pl.momentum if abs(pl.momentum) > self.speed else -self.speed)
        else:
            pl.turn_left(-self.speed + pl.momentum)                
            pl.step_momentum()
                
            #endif
        #endif
        
    def cancel_move(self):
        
        pl = self.player
        pl.set_horizontal_speed(abs(pl.momentum))
        pl.step_momentum()            
        
        
    def cancel_jump(self):
        
        if self.player.vertical_speed < 0: 
            self.player.vertical_speed = 0 
    
    def enter(self):
        self.player.set_vertical_speed(self.player.properties.jump_speed)
        self.player.set_current_animation_key(StateKeys.JUMPING)
        self.player.midair_dash_countdown = self.player.properties.max_midair_dashes
        self.player.range_collision_group.add(self.range_sprite) 
        
        
    def exit(self):
        self.player.range_collision_group.remove(self.range_sprite)                
        self.edge_in_reach = False  
        self.has_landed = False
        
    def check_landing(self,platform):
        
        # check if near edge
        ps = self.player                
        w = ps.rect.width
        min = w*0.5
        
        # finding side of platform
        on_platform_right = ps.rect.centerx > platform.rect.centerx
        
        # standing on left edge
        distance  = abs(platform.rect.right - ps.rect.left ) \
        if on_platform_right else abs(ps.rect.right - platform.rect.left)
        
        self.has_landed = True                
        if distance < min:                
            if on_platform_right:
                ps.rect.right = platform.rect.right+min
                
            else:
                ps.rect.left = platform.rect.left-min
            
            #endif                    
        #endif
            
        
    def get_hang_sprite(self):


        if self.player.facing_right:
            self.hang_sprite.rect.centerx = self.player.rect.right
            self.hang_sprite.rect.centery = self.player.rect.top
        else :
            self.hang_sprite.rect.centerx = self.player.rect.left
            self.hang_sprite.rect.centery = self.player.rect.top
        
        return self.hang_sprite  
        
    def check_near_edge(self,platforms):
        
        if self.player.vertical_speed < 0:
            return
        
        
        # check for reachable edges
        ps = self.player
        hs = self.get_hang_sprite()
                    
        # must be below platform top                
        self.edge_in_reach = False   
        for platform in platforms:
            if (ps.rect.bottom > platform.rect.bottom):
                
                if self.player.facing_right and hs.rect.collidepoint(platform.rect.topleft) :                            
                    self.edge_in_reach = True  
                    self.player.nearby_platforms.empty()
                    self.player.nearby_platforms.add(platform)
                    break
                
                if (not self.player.facing_right) and hs.rect.collidepoint(platform.rect.topright):                            
                    self.edge_in_reach = True  
                    self.player.nearby_platforms.empty()
                    self.player.nearby_platforms.add(platform) 
                    break
                             
                 
                #endif                    
                
            #endif
            
        #endfor   
    
        
class FallState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.FALLING,player)
        
        self.speed = 0
                
        self.edge_in_reach = False  
        self.has_landed = False  
        self.hang_sprite = pygame.sprite.Sprite()         
        
        self.add_action(PlayerActionKeys.CANCEL_MOVE,lambda : self.cancel_move())
        self.add_action(LevelActionKeys.APPLY_GRAVITY,lambda g: self.player.apply_gravity(g))
        self.add_action(PlayerActionKeys.MOVE_LEFT,lambda : self.turn_left())
        self.add_action(PlayerActionKeys.MOVE_RIGHT,lambda : self.turn_right())   
        self.add_action(LevelActionKeys.COLLISION_BELOW,self.check_landing)
        self.add_action(LevelActionKeys.COLLISION_RIGHT_WALL,lambda platform : self.player.set_momentum(0))
        self.add_action(LevelActionKeys.COLLISION_LEFT_WALL,lambda platform : self.player.set_momentum(0)) 
        self.add_action(LevelActionKeys.PLATFORMS_IN_RANGE,lambda platforms: self.check_near_edge(platforms))  
        
        
    def setup(self,asset):
        
        self.hang_sprite.rect =  pygame.Rect(0,0,2*self.player.properties.hang_radius,
                                                 2*self.player.properties.hang_radius) 
        
        self.speed = self.player.properties.run_speed
        
        
        # creating range rectangle
        self.range_sprite = pygame.sprite.Sprite()
        self.range_sprite.rect = self.player.rect.copy()
        self.range_sprite.rect.width = self.range_sprite.rect.width + self.hang_sprite.rect.width
        self.range_sprite.rect.height = self.range_sprite.rect.height + self.hang_sprite.rect.height 
        
    def turn_right(self):
        
        pl = self.player
        if pl.momentum >0:
        
            pl.turn_right(pl.momentum if pl.momentum > self.speed else self.speed)
        else:
            pl.turn_right(self.speed + pl.momentum)                
            pl.step_momentum()
                
            #endif
        #endif
            
        
    def turn_left(self):
        
        pl = self.player
        if pl.momentum <0:
        
            pl.turn_left(pl.momentum if abs(pl.momentum) > self.speed else -self.speed)
        else:
            pl.turn_left(-self.speed + pl.momentum)                
            pl.step_momentum()
                
            #endif
        #endif  
        
    def cancel_move(self):        
        
        pl = self.player
        pl.set_horizontal_speed(abs(pl.momentum))
        pl.step_momentum()  

    
    def enter(self):
            
        self.player.set_current_animation_key(StateKeys.FALLING)
        self.player.range_collision_group.add(self.range_sprite)
        
        
        
    def exit(self):
        self.player.range_collision_group.remove(self.range_sprite)
        self.edge_in_reach = False 
        self.has_landed = False
        
    def check_landing(self,platform):
        
        # check if near edge
        ps = self.player                
        w = ps.rect.width
        min = w*0.5
        
        # finding side of platform
        on_platform_right = ps.rect.centerx > platform.rect.centerx
        
        # standing on left edge
        distance  = abs(platform.rect.right - ps.rect.left ) \
        if on_platform_right else abs(ps.rect.right - platform.rect.left)

        
        
        self.has_landed = True
        
        if distance < min:                    
            if on_platform_right:
                ps.rect.right = platform.rect.right+min
                
            else:
                ps.rect.left = platform.rect.left-min
            
            #endif
            
        #endif
            
        
    def get_hang_sprite(self):        

        if self.player.facing_right:
            self.hang_sprite.rect.centerx = self.player.rect.right
            self.hang_sprite.rect.centery = self.player.rect.top
        else :
            self.hang_sprite.rect.centerx = self.player.rect.left
            self.hang_sprite.rect.centery = self.player.rect.top
        
        return self.hang_sprite  
    
    def check_near_edge(self,platforms):
        
        
        # check for reachable edges
        ps = self.player
        hs = self.get_hang_sprite()
                    
        # must be below platform top
        self.edge_in_reach = False 
        for platform in platforms:
            if (ps.rect.bottom > platform.rect.bottom):
                
                if self.player.facing_right and hs.rect.collidepoint(platform.rect.topleft) :
                    self.edge_in_reach = True
                    self.player.nearby_platforms.empty()
                    self.player.nearby_platforms.add(platform)
                    break
                
                if (not self.player.facing_right) and hs.rect.collidepoint(platform.rect.topright):
                    self.edge_in_reach = True
                    self.player.nearby_platforms.empty()
                    self.player.nearby_platforms.add(platform)
                    break
                             
                 
                #endif                    
                
            #endif
            
        #endfor
        
        return
    
class LandState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.LANDING,player)
        
        self.apply_momentum_reduction = False
        
        
    def enter(self):                

        self.player.midair_dash_countdown = self.player.properties.max_midair_dashes
        
        self.player.set_current_animation_key(StateKeys.LANDING)           
        
        self.player.vertical_speed = 0
        self.player.horizontal_speed = 0
        self.player.set_momentum(0)       
        
class HangingState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.HANGING,player)
        
        self.platform_rect = None
        
        self.add_action(PlayerActionKeys.ACTION_SEQUENCE_EXPIRED,
                            lambda : self.player.set_current_animation_key(StateKeys.HANGING,[-1]))        
        
        
    def hang(self,platform):
        
        if self.platform_rect != platform.rect:
            
            self.platform_rect = platform.rect
            
            if self.player.facing_right:
                self.player.rect.right = self.platform_rect.left - \
                self.player.properties.hang_distance_from_side
            else:
                self.player.rect.left = self.platform_rect.right + \
                self.player.properties.hang_distance_from_side
            
            #endif
                
            self.player.rect.top = self.platform_rect.top + self.player.properties.hang_distance_from_top
                    
    def enter(self):
        
        self.player.set_current_animation_key(StateKeys.HANGING)
        self.player.set_horizontal_speed(0)
        self.player.set_vertical_speed(0)
        self.player.set_momentum(0)
        self.hang(self.player.nearby_platforms.sprites()[0])
        
    def exit(self):
        
        self.platform_rect = None
        
class ClimbingState(BasicState):
    
    def __init__(self,player):
        
        BasicState.__init__(self,StateKeys.CLIMBING,player)
        self.platform_rect = None
        self.climb_path =[]
        
        self.add_action(LevelActionKeys.STEP_GAME,lambda time_elapsed :self.climb())
        
    def enter(self):
        self.player.set_current_animation_key(StateKeys.CLIMBING)
        self.player.set_horizontal_speed(0)
        self.player.set_vertical_speed(0)
        self.player.set_momentum(0)
        
        self.platform_rect = self.player.nearby_platforms.sprites()[0].rect
        

        ply_rect = self.player.rect
        plt_rect = self.platform_rect
        
        # saving initial position relative to platform
        self.startx = self.player.properties.climb_distance_from_side + ply_rect.width
        self.startx = (-self.startx ) if self.player.facing_right else (self.startx)
        
        # start y value of rect bottom
        self.starty =  self.player.properties.climb_distance_from_top +ply_rect.height                

        # calculating distances
        dx = -self.startx
        dy = -self.starty
        #self.start_pos = ply_rect.center
        
        # creating path
        self.climb_path =[(0,0),
                          (0,0),
                          (0,dy/3.0),
                          (0,2*dy/3.0),
                          (0,dy),
                          (dx/2.0,dy),
                          (dx,dy),
                          (dx,dy),
                          (dx,dy)]
        
    def exit(self):                
        self.player.nearby_platforms.empty()
        
    def climb(self):
        
        dx = 0
        dy = 0
        if self.player.facing_right:
            dx = self.platform_rect.left + self.startx +  self.climb_path[self.player.animation_frame_index][0]
            self.player.rect.left = dx
            
        else:
            dx = self.platform_rect.right + self.startx + self.climb_path[self.player.animation_frame_index][0]
            self.player.rect.right = dx
        
        dy = self.platform_rect.top + self.starty + self.climb_path[self.player.animation_frame_index][1]
        self.player.rect.bottom= dy
        
        
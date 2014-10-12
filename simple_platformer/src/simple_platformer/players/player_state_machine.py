from simple_platformer.game_object import AnimatableObject
from simple_platformer.players import AnimatablePlayer
from simple_platformer.players import PlayerProperties
from simple_platformer.game_state_machine import *
import pygame

class PlayerStateMachine(AnimatablePlayer,StateMachine):
         
    class StateKeys:
    
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
    
    def __init__(self):
        
        # superclass constructors
        AnimatablePlayer.__init__(self)
        StateMachine.__init__(self)
        
        # registering handler
        self.add_event_handler(AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED,self.action_sequence_expired_handler)
        
    def setup(self,sprite_desc_file):
        
        if not AnimatablePlayer.setup(self,sprite_desc_file):
            return False
        
        self.create_transition_rules()
        
        return True
        
    def action_sequence_expired_handler(self):
            self.execute(ActionKeys.ACTION_SEQUENCE_EXPIRED)
        
        
    def create_transition_rules(self):
        
        # run state
        class RunningState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.RUNNING)
                
                self.player = player
                self.speed = self.player.player_properties.run_speed
                
                self.add_action(ActionKeys.MOVE_LEFT,lambda : self.player.turn_left(-self.speed))
                self.add_action(ActionKeys.MOVE_RIGHT,lambda : self.player.turn_right(self.speed))
                
            
            def enter(self):
                
                self.player.player_properties.max_step_x = self.speed            
                self.player.set_current_animation_key(ActionKeys.RUN),
                self.player.set_forward_speed(self.speed)  
                
            def exit(self):
                self.player.player_properties.max_step_x = self.player.player_properties.dash_speed         
        run_state = RunningState(self)
        
        
        # dash state
        dash_state = State(PlayerStateMachine.StateKeys.DASHING)
        dash_state.set_entry_callback(lambda: self.dash())
        dash_state.set_exit_callback(lambda: self.set_inertia(0.8*self.player_properties.dash_speed 
                                                              if self.get_animation_progress_percentage()>0.3 else 0))
        
        # midair dash state
        midair_dash_state = State(PlayerStateMachine.StateKeys.MIDAIR_DASHING)
        midair_dash_state.set_exit_callback(lambda: self.set_inertia(self.player_properties.dash_speed * 
                                                                     self.get_animation_progress_percentage()))
        midair_dash_state.set_entry_callback(lambda: self.midair_dash())
        
        # dash breaking 
        dash_breaking_state = State(PlayerStateMachine.StateKeys.DASH_BREAKING)
        dash_breaking_state.set_entry_callback(lambda:self.dash_break( self.player_properties.run_speed))
        dash_breaking_state.set_exit_callback(lambda: self.set_inertia(0))
        dash_breaking_state.add_action(ActionKeys.ACTION_SEQUENCE_EXPIRED,
                                    lambda : self.set_current_animation_key(ActionKeys.DASH_BREAK,[-1])) #last frame
        
        
        # stand state        
        class StandState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.STANDING)
                self.player = player
                self.is_standing_on_edge = False
                self.is_beyond_edge = False
                
                # creating range rectangle
                self.range_sprite = pygame.sprite.Sprite()
                self.range_sprite.rect = self.player.rect.copy()
                self.range_sprite.rect.height = self.range_sprite.rect.height + 4
                
                self.add_action(ActionKeys.PLATFORMS_IN_RANGE,lambda platforms: self.check_near_edge(platforms)) 
                
            def enter(self):
                
                self.player.set_forward_speed(0)
                self.player.set_current_animation_key(ActionKeys.STAND)
                self.player.set_inertia(0)
                self.player.midair_dash_countdown = self.player.player_properties.max_midair_dashes
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
                    max = w*self.player.player_properties.max_distance_from_edge
                    min = w*self.player.player_properties.min_distance_from_edge
                    
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
        
        stand_state = StandState(self)
        
        # stand edge state
        stand_edge_state = self.create_base_game_state(PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                                                 0, None, None)
        stand_edge_state.set_entry_callback(lambda: (
                                       self.set_current_animation_key(ActionKeys.STAND_EDGE),
                                       self.set_forward_speed(0)))
        stand_edge_state.add_action(ActionKeys.ACTION_SEQUENCE_EXPIRED,
                                    lambda : self.set_current_animation_key(ActionKeys.STAND_EDGE,[-1])) #last frame

        # jump state
        class JumpState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.JUMPING)
                
                self.player = player
                self.speed = self.player.player_properties.run_speed
                
                self.has_landed = False
                self.edge_in_reach = False                   
                self.hang_sprite = pygame.sprite.Sprite()
                self.hang_sprite.rect =  pygame.Rect(0,0,2*self.player.player_properties.hang_radius,
                                                         2*self.player.player_properties.hang_radius) 
                
                # creating range rectangle
                self.range_sprite = pygame.sprite.Sprite()
                self.range_sprite.rect = self.player.rect.copy()
                self.range_sprite.rect.width = self.range_sprite.rect.width + self.hang_sprite.rect.width
                self.range_sprite.rect.height = self.range_sprite.rect.height + self.hang_sprite.rect.height
                
                self.add_action(ActionKeys.MOVE_LEFT,lambda : self.player.turn_left(-self.speed))
                self.add_action(ActionKeys.MOVE_RIGHT,lambda : self.player.turn_right(self.speed))                
                self.add_action(ActionKeys.CANCEL_MOVE,lambda : self.player.set_forward_speed(0))
                self.add_action(ActionKeys.CANCEL_JUMP,lambda : self.cancel_jump())
                self.add_action(ActionKeys.APPLY_GRAVITY,lambda g: self.player.apply_gravity(g))    
                self.add_action(ActionKeys.COLLISION_BELOW,self.check_landing)
                self.add_action(ActionKeys.COLLISION_RIGHT_WALL,lambda platform : self.player.set_inertia(0))
                self.add_action(ActionKeys.COLLISION_LEFT_WALL,lambda platform : self.player.set_inertia(0)) 
                self.add_action(ActionKeys.PLATFORMS_IN_RANGE,lambda platforms: self.check_near_edge(platforms))  
                
                
            def cancel_jump(self):
                
                if self.player.current_upward_speed < 0: 
                    self.player.current_upward_speed = 0 
            
            def enter(self):
                self.player.set_upward_speed(self.player.player_properties.jump_speed)
                self.player.set_current_animation_key(ActionKeys.JUMP)
                self.player.midair_dash_countdown = self.player.player_properties.max_midair_dashes
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
                
                if self.player.current_upward_speed < 0:
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
                            self.player.near_platforms.empty()
                            self.player.near_platforms.add(platform)
                            break
                        
                        if (not self.player.facing_right) and hs.rect.collidepoint(platform.rect.topright):                            
                            self.edge_in_reach = True  
                            self.player.near_platforms.empty()
                            self.player.near_platforms.add(platform) 
                            break
                                     
                         
                        #endif                    
                        
                    #endif
                    
                #endfor   
        
        jump_state = JumpState(self)
        
        
        # fall state
        class FallState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.FALLING)
                
                self.player = player
                
                self.edge_in_reach = False  
                self.has_landed = False  
                self.hang_sprite = pygame.sprite.Sprite()
                self.hang_sprite.rect =  pygame.Rect(0,0,2*self.player.player_properties.hang_radius,
                                                         2*self.player.player_properties.hang_radius) 
                # creating range rectangle
                self.range_sprite = pygame.sprite.Sprite()
                self.range_sprite.rect = self.player.rect.copy()
                self.range_sprite.rect.width = self.range_sprite.rect.width + self.hang_sprite.rect.width
                self.range_sprite.rect.height = self.range_sprite.rect.height + self.hang_sprite.rect.height
                
                self.add_action(ActionKeys.CANCEL_MOVE,lambda : self.player.set_forward_speed(0))
                self.add_action(ActionKeys.APPLY_GRAVITY,lambda g: self.player.apply_gravity(g))
                self.add_action(ActionKeys.MOVE_LEFT,lambda : self.player.turn_left(-self.player.player_properties.run_speed))
                self.add_action(ActionKeys.MOVE_RIGHT,lambda : self.player.turn_right(self.player.player_properties.run_speed))
                self.add_action(ActionKeys.COLLISION_BELOW,self.check_landing)
                self.add_action(ActionKeys.COLLISION_RIGHT_WALL,lambda platform : self.player.set_inertia(0))
                self.add_action(ActionKeys.COLLISION_LEFT_WALL,lambda platform : self.player.set_inertia(0)) 
                self.add_action(ActionKeys.PLATFORMS_IN_RANGE,lambda platforms: self.check_near_edge(platforms))   
                
        
            
            def enter(self):
                
                if self.player.current_upward_speed < 0:
                    self.player.current_upward_speed = 0
            
                self.player.set_current_animation_key(ActionKeys.FALL)
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
                            self.player.near_platforms.empty()
                            self.player.near_platforms.add(platform)
                            break
                        
                        if (not self.player.facing_right) and hs.rect.collidepoint(platform.rect.topright):
                            self.edge_in_reach = True
                            self.player.near_platforms.empty()
                            self.player.near_platforms.add(platform)
                            break
                                     
                         
                        #endif                    
                        
                    #endif
                    
                #endfor
                
                return
                
                
        fall_state = FallState(self)
          
        
        # land state
        class LandState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.LANDING)
                self.player = player
                
            def enter(self):                
        
                self.player.midair_dash_countdown = self.player.player_properties.max_midair_dashes
                
                self.player.set_current_animation_key(ActionKeys.LAND)
                
                if (self.player.current_upward_speed + self.player.current_inertia) < 0 and self.player.current_inertia > 0:
                    self.player.current_inertia = 0
                elif (self.player.current_upward_speed + self.player.current_inertia) > 0 and self.player.current_inertia < 0:
                    self.player.current_inertia = 0
                #endif
                
                self.player.current_upward_speed = 0
                self.player.current_forward_speed = 0
                
        land_state = LandState(self)
        
        # hanging state
        class HangingState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.HANGING)
                
                self.player = player
                self.platform_rect = None
                
                self.add_action(ActionKeys.ACTION_SEQUENCE_EXPIRED,
                                    lambda : self.player.set_current_animation_key(ActionKeys.HANG,[-1])) 
                
                
                
            def hang(self,platform):
                
                if self.platform_rect != platform.rect:
                    
                    self.platform_rect = platform.rect
                    
                    if self.player.facing_right:
                        self.player.rect.right = self.platform_rect.left - \
                        self.player.player_properties.hang_distance_from_side
                    else:
                        self.player.rect.left = self.platform_rect.right + \
                        self.player.player_properties.hang_distance_from_side
                    
                    #endif
                        
                    self.player.rect.top = self.platform_rect.top + self.player.player_properties.hang_distance_from_top
                    
                print "Hanging at top point %i"%(self.player.rect.top)
                
            def enter(self):
                
                self.player.set_current_animation_key(ActionKeys.HANG)
                self.player.set_forward_speed(0)
                self.player.set_upward_speed(0)
                self.player.set_inertia(0)
                self.hang(self.player.near_platforms.sprites()[0])
                
            def exit(self):
                
                self.platform_rect = None
                
        
        hanging_state = HangingState(self)
                
        
        # climbing state
        class ClimbingState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.CLIMBING)
                self.player = player
                self.platform_rect = None
                self.climb_path =[]
                
                self.add_action(ActionKeys.STEP_GAME,self.climb)
                
            def enter(self):
                self.player.set_current_animation_key(ActionKeys.CLIMB)
                self.player.set_forward_speed(0)
                self.player.set_upward_speed(0)
                self.player.set_inertia(0)
                
                self.platform_rect = self.player.near_platforms.sprites()[0].rect
                

                ply_rect = self.player.rect
                plt_rect = self.platform_rect
                
                # saving initial position relative to platform
                self.startx = self.player.player_properties.climb_distance_from_side + ply_rect.width
                self.startx = (-self.startx ) if self.player.facing_right else (self.startx)
                
                # start y value of rect bottom
                self.starty =  self.player.player_properties.climb_distance_from_top +ply_rect.height                

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
                self.player.near_platforms.empty()
                
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
                
        climbing_state = ClimbingState(self)
                            

        
        # transitions
        sm = self
        
        sm.add_transition(run_state,ActionKeys.CANCEL_MOVE,PlayerStateMachine.StateKeys.STANDING)
        sm.add_transition(run_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(run_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(run_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING)
        sm.add_transition(run_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: self.current_inertia > 0)
        sm.add_transition(run_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: self.current_inertia < 0)
        
        
        sm.add_transition(dash_state,ActionKeys.CANCEL_DASH,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: self.get_animation_progress_percentage()>0.2)
        sm.add_transition(dash_state,ActionKeys.CANCEL_DASH,PlayerStateMachine.StateKeys.RUNNING,
                          lambda: not (self.get_animation_progress_percentage()>0.2))
        sm.add_transition(dash_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(dash_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.RUNNING)
        
        
        sm.add_transition(midair_dash_state,ActionKeys.CANCEL_DASH,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(midair_dash_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.FALLING)
        
        sm.add_transition(dash_breaking_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING,
                          lambda: not self.facing_right)
        sm.add_transition(dash_breaking_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING,
                          lambda: self.facing_right)
        sm.add_transition(dash_breaking_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(dash_breaking_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_breaking_state,ActionKeys.STEP_GAME,PlayerStateMachine.StateKeys.STANDING,
                          lambda: self.current_inertia == 0)
        
        
        sm.add_transition(stand_state,ActionKeys.RUN,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(stand_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING)
        sm.add_transition(stand_state,ActionKeys.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                          lambda: stand_state.is_standing_on_edge)
        sm.add_transition(stand_state,ActionKeys.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.FALLING,
                  lambda: stand_state.is_beyond_edge)
        
        
        sm.add_transition(stand_edge_state,ActionKeys.RUN,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(stand_edge_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_edge_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING)
        
        sm.add_transition(jump_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_countdown > 0)
        sm.add_transition(jump_state,ActionKeys.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING,
                          lambda : jump_state.has_landed)
        sm.add_transition(jump_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_ABOVE,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.HANGING,
                          lambda : jump_state.edge_in_reach)
        
        sm.add_transition(fall_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_countdown > 0)
        sm.add_transition(fall_state,ActionKeys.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(fall_state,ActionKeys.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING,
                          lambda : fall_state.has_landed)
        sm.add_transition(fall_state,ActionKeys.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.HANGING,
                          lambda : fall_state.edge_in_reach)
        
        sm.add_transition(hanging_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING,
                          lambda : self.get_animation_progress_percentage()>0.2) 
        sm.add_transition(hanging_state,ActionKeys.MOVE_UP,PlayerStateMachine.StateKeys.CLIMBING,
                          lambda : self.get_animation_progress_percentage()>=1) 
        
        sm.add_transition(climbing_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.STANDING) 
        
        
        sm.add_transition(land_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.STANDING)  
        sm.add_transition(land_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING,
                          lambda : self.get_animation_progress_percentage()>0.2)  
        sm.add_transition(land_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING,
                          lambda : self.get_animation_progress_percentage()>0.2)
        sm.add_transition(land_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING) 
        
        
        
    def create_base_game_state(self,state_key,move_speed,entry_cb = None,exit_cb = None):
        
        state = State(state_key)
        state.set_entry_callback(entry_cb)
        state.set_exit_callback(exit_cb)
        
        state.add_action(ActionKeys.MOVE_LEFT,lambda : self.turn_left(-move_speed))
        state.add_action(ActionKeys.MOVE_RIGHT,lambda : self.turn_right(move_speed))
        
        return state
import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import SubStateMachine
from simple_platformer.game_object import AnimatableObject
from combat_platformer.player.action_keys import PlayerActionKeys
from combat_platformer.level.action_keys import LevelActionKeys
from combat_platformer.enemy import EnemyProperties
from combat_platformer.enemy import EnemyBase
from simple_platformer.game_object.collision_masks import CollisionMasks

class StateKeys(object):
    
    PATROL = 'PATROL'
    ALERT='ALERT'
    CHASE='CHASE'
    RUN = 'RUN'
    WALK = 'WALK'
    JUMP='JUMP'
    UNWARY='UNWARY'
    DROP='DROP'
    WIPEOUT='WIPEOUT'
    STANDUP = 'STANDUP'
    STAND = 'STAND'
    
    
class BasicState(State):
    
    LA = LevelActionKeys
    PA = PlayerActionKeys
    
    
    def __init__(self,key,game_object):
        
        State.__init__(self,key)
        self.game_object = game_object  
        
    def setup(self,assets):
        
        print "setup method for state %s is unimplemented"%(self.key)    


        
class RunState(BasicState):
    
    def __init__(self,game_object):
        
        BasicState.__init__(self,StateKeys.RUN,self.game_object)        
        self.speed = 0 
        
    def enter(self):
                 
        self.game_object.set_current_animation_key(StateKeys.RUN)
        
    def setup(self,assets):
        
        self.speed = self.game_object.properties.run_speed
        self.add_action(BasicState.LA.STEP_GAME, lambda : self.update())   
        
    def update(self):
        pass
        
class JumpState(BasicState):
    
    def __init__(self,game_object):
        
        BasicState.__init__(self,StateKeys.JUMP,game_object)        
              
        self.has_landed = False
                      
        
    def setup(self,asset):
        
        self.speed = self.game_object.properties.jump_speed 
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update())  
        self.add_action(BasicState.LA.APPLY_GRAVITY,lambda g: self.game_object.apply_gravity(g))    
        self.add_action(BasicState.LA.PLATFORM_COLLISION_ABOVE,lambda platform : self.game_object.set_vertical_speed(0))
        self.add_action(BasicState.LA.PLATFORM_COLLISION_RIGHT,lambda platform : self.game_object.set_momentum(0))
        self.add_action(BasicState.LA.PLATFORM_COLLISION_LEFT,lambda platform : self.game_object.set_momentum(0)) 

    def update(self):
        pass
    
    def enter(self):        
        
        self.game_object.set_vertical_speed(self.speed)
        self.game_object.set_current_animation_key(StateKeys.JUMPING)
        self.game_object.midair_dash_remaining = self.game_object.properties.max_midair_dashes
        self.game_object.range_collision_group.add(self.range_sprite) 
        
    def exit(self):
        self.game_object.range_collision_group.remove(self.range_sprite)      
        self.has_landed = False
        
class DropState(BasicState):
    
    def __init__(self,game_object):
        BasicState.__init__(self, StateKeys.DROP , game_object)
                        
        self.add_action(LevelActionKeys.APPLY_GRAVITY,lambda g: self.game_object.apply_gravity(g))
        self.add_action(AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED,
                lambda : self.game_object.set_current_animation_key(StateKeys.DROP,[-1]))
        
    def setup(self,asset):
        pass
    
    def enter(self):
            
        self.game_object.set_current_animation_key(StateKeys.DROP)
        self.game_object.set_horizontal_speed(0)
        
class WipeoutState(BasicState):
    
    def __init__(self,game_object):
        
        BasicState.__init__(self, StateKeys.WIPEOUT, game_object)
        self.time_down = 2000
        self.time_left = 0
        self.time_consumed = False
        self.start_consume_time = False
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))
        self.add_action(AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED,
                lambda : self.animation_expired())
        
    def enter(self):
        self.game_object.set_current_animation_key(StateKeys.WIPEOUT)
        self.game_object.set_vertical_speed(0)
        self.time_left = self.time_down
        self.start_consume_time = False
        self.time_consumed = False
        
    def animation_expired(self):
        self.start_consume_time = True
        self.game_object.set_current_animation_key(StateKeys.WIPEOUT,[-1])
        
    def update(self,time_elapsed):
        
        if self.start_consume_time:
            self.time_left-=time_elapsed
            
            if self.time_left <= 0:
                self.time_consumed = True
            #endif
        #endif
        
class StandupState(BasicState):
    
    def __init__(self,game_object):
        BasicState.__init__(self, StateKeys.STANDUP, game_object)
        
    def enter(self):
        self.game_object.set_current_animation_key(StateKeys.STANDUP)
                  
        
class AlertState(BasicState):
    
    def __init__(self,game_object):
        BasicState.__init__(self,StateKeys.ALERT,game_object) 
        
        self.time_active = 10
        self.time_left = 10
        self.time_consumed = False
        self.alert_area_sprite = pygame.sprite.Sprite()
        
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))
        
    def setup(self,assets):
        
        self.time_active = self.game_object.properties.alert_time
        
        pr = self.game_object.rect
        self.alert_area_sprite.rect = self.game_object.properties.sight_area_rect
        self.alert_area_sprite.offset = (0,(pr.height - self.alert_area_sprite.rect.height)/2)
        
    def update(self,time_elapsed):
        
        if self.is_player_in_area():
            
            self.face_player()
            
            #reset time
            self.time_left = self.time_active
        else:
            
            self.time_left -= time_elapsed
            
            if self.time_left <= 0:
                self.time_consumed = True
            #endif
        #endif
        
    def face_player(self):
        ps = self.game_object.target_object
        cs = self.game_object
        
        if ps.rect.centerx > cs.rect.centerx:
            cs.turn_right(0)
        elif ps.rect.centerx < cs.rect.centerx:
            cs.turn_left(0)
        #endif
            
    
    def is_player_in_area(self):
        
        ps = self.game_object.target_object
        ar = self.alert_area_sprite
        cs = self.game_object
        
        ar.rect.centerx = cs.rect.centerx + ar.offset[0]
        ar.rect.centery = cs.rect.centery + ar.offset[1]
        
        return pygame.sprite.collide_rect(ps, ar)
    
    def enter(self):
        
        self.time_left = self.time_active
        self.time_consumed = False
        
        self.game_object.set_horizontal_speed(0)
        self.game_object.set_current_animation_key(StateKeys.ALERT)
        
    
class PatrolState(SubStateMachine):
    
    class WalkState(BasicState):
    
        MAX_ENCOUNTERS = 4
        
        def __init__(self,game_object):
            
            BasicState.__init__(self,StateKeys.WALK,game_object)      
              
            self.speed = 0 
            self.encounters = 0
            self.patrol_rect = None
            self.time_active = 10000
            self.time_left = 10000
            self.time_consumed = False
            self.player_sighted = False
            self.support_platform = None
            self.found_obstacle = False
            self.pause_walk = False
            
              
            self.sight_sprite = pygame.sprite.Sprite()
            self.range_sprite = pygame.sprite.Sprite()              
            
            self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))    
            self.add_action(BasicState.LA.PLATFORM_COLLISION_RIGHT, lambda platforms : self.turn_around(True))
            self.add_action(BasicState.LA.PLATFORM_COLLISION_LEFT, lambda platforms : self.turn_around(False))
            self.add_action(BasicState.LA.GAME_OBJECT_COLLISION_RIGHT,
                             lambda game_obj : self.object_encountered(game_obj,True))
            self.add_action(BasicState.LA.GAME_OBJECT_COLLISION_LEFT,
                             lambda game_obj : self.object_encountered(game_obj,False))
            self.add_action(BasicState.LA.PLATFORMS_IN_RANGE, lambda platforms : self.set_support_platform(platforms))
            
            self.add_action(BasicState.LA.GAME_OBJECT_IN_RANGE,
                            lambda player,range_sprites : self.check_player_insight(player,range_sprites))
            
        def enter(self):
                                 
            self.time_left = self.time_active
            self.time_consumed = False
            self.player_sighted = False
            self.support_platforms = None
            self.found_obstacle = False
            self.pause_walk = False
            self.encounters = 0
                    
            self.game_object.set_current_animation_key(StateKeys.WALK)
            self.game_object.range_collision_group.add(self.range_sprite)
            self.game_object.range_collision_group.add(self.sight_sprite)
            self.game_object.set_horizontal_speed(self.speed)
            
        def exit(self):
            self.game_object.range_collision_group.remove(self.range_sprite)
            self.game_object.range_collision_group.remove(self.sight_sprite)
                        
        def setup(self,assets):
            
            self.speed = self.game_object.properties.walk_speed  
            self.patrol_rect  = self.game_object.properties.patrol_area_rect
            self.time_active = self.game_object.properties.patrol_walk_time
            
            # sight sprite
            pr = self.game_object.rect
            self.sight_sprite.rect = pygame.Rect(0,0,300,100) 
            self.sight_sprite.offset = (0,(pr.height - self.sight_sprite.rect.height)/2)
            
            # range sprite
            self.range_height_extension = 4
            self.range_sprite.rect = self.game_object.rect.copy()
            self.range_sprite.rect.height = self.range_sprite.rect.height + self.range_height_extension
            self.range_sprite.offset = (0,0)
            
        def set_support_platform(self,platforms):
            go = self.game_object
            for p in platforms:
                if abs(go.rect.bottom - p.rect.top) <=2:                    
                    self.support_platform = p
                #endif
            #endfor
            
        def object_encountered(self,game_obj, collision_right):
                        
            if game_obj.type_bitmask != CollisionMasks.ENEMY:
                return
            #endif
            
            
            self.found_obstacle = True
            self.encounters +=1
            
            if self.game_object.facing_right == collision_right:                
                if self.game_object.facing_right:
                    self.game_object.rect.right = game_obj.rect.left
                    self.game_object.turn_left(-self.speed)
                else :
                    self.game_object.rect.left = game_obj.rect.right
                    self.game_object.turn_right(self.speed)
            #endif
            
            if self.encounters > PatrolState.WalkState.MAX_ENCOUNTERS:
                self.pause_walk = True
            #endif
                
            
    
        def turn_around(self,collision_right):
            
            self.found_obstacle = True
            if self.game_object.facing_right == collision_right:
                
                if self.game_object.facing_right:
                    self.game_object.turn_left(-self.speed)
                else :
                    self.game_object.turn_right(self.speed)
                #endif
                
            #endif
            
        def return_to_patrol_area(self):
            
            ps = self.game_object  
            if self.support_platform != None:
                if ps.rect.centerx > self.support_platform.rect.centerx:
                    ps.turn_left(-self.speed)
                else:
                    ps.turn_right(self.speed)
                #endif
            #endif
                
            
        def is_inside_patrol_area(self):
            
            ps = self.game_object            
            in_area = True
            if self.support_platform != None:
                self.patrol_rect.bottom = self.support_platform.rect.top
                self.patrol_rect.centerx = self.support_platform.rect.centerx
                in_area = self.patrol_rect.colliderect(ps.rect)
            #endif
            
            return in_area 
                
        def check_player_insight(self,game_object,range_sprites):
            
            if game_object.type_bitmask != CollisionMasks.PLAYER:
                return
            #endif
            
            go = self.game_object
            pl = game_object
            for sp in range_sprites:
                
                if sp == self.sight_sprite:                    
                    if self.game_object.facing_right and (go.rect.centerx < pl.rect.centerx):
                        self.game_object.target_object = pl
                        self.player_sighted = True
                    
                    elif (not self.game_object.facing_right) and (go.rect.centerx > pl.rect.centerx):
                        self.game_object.target_object = pl
                        self.player_sighted = True
                        
                    #endif
                    
                    break
                
                #endif
            #endfor                   

            
        def update(self,time_elapsed):
                     
            # update time counter
            self.time_left -= time_elapsed
            
                # check active time
            if self.time_left <= 0:
                self.time_consumed = True
            else:
            
                if (not self.found_obstacle) and (not self.is_inside_patrol_area()):                        
                    self.return_to_patrol_area()
                #endif        
            #endif
            
    class UnwaryState(BasicState):
        
        STATE_WIDTH = 110
        def __init__(self,game_object):
            
            BasicState.__init__(self,StateKeys.UNWARY,game_object)
            
            self.time_active = 10000
            self.time_left = 10000 
            self.time_consumed = False
            
            self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))  
            self.add_action(AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED,
                            lambda : self.game_object.set_current_animation_key(StateKeys.UNWARY,[-1]))
            
        def enter(self):      
            
            self.game_object.width = PatrolState.UnwaryState.STATE_WIDTH
            self.game_object.set_current_animation_key(StateKeys.UNWARY)
            self.time_left = self.time_active
            self.time_consumed = False  
            self.game_object.set_horizontal_speed(0) 
            
        def exit(self):
            
            self.game_object.width = self.game_object.properties.collision_width
        
        def setup(self,assets):
            
            self.time_active = self.game_object.properties.patrol_unwary_time
            
        def update(self,time_elapsed):
            
            self.time_left -= time_elapsed
            if self.time_left <= 0:
                
                print 'UNWARY state time consumed, time elapsed %i'%(time_elapsed)
                self.time_consumed = True
            #endif  
            
    class StandState(BasicState):
        
        def __init__(self,game_object):
            
            BasicState.__init__(self,StateKeys.STAND,game_object)
            
            self.time_active = 1000
            self.time_left = 1000 
            self.time_consumed = False
            
            self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))  
            
        def enter(self):      
            
            self.game_object.set_current_animation_key(self.key)
            self.time_left = self.time_active
            self.time_consumed = False  
            self.game_object.set_horizontal_speed(0) 
        
        def setup(self,assets):
            pass
            
        def update(self,time_elapsed):
            
            self.time_left -= time_elapsed
            if self.time_left <= 0:
                
                print 'PATROL::WALK state time consumed, time elapsed %i'%(time_elapsed)
                self.time_consumed = True              
    
    
    def __init__(self,parent_sm,game_object):
        
        SubStateMachine.__init__(self,StateKeys.PATROL ,parent_sm)
        self.game_object = game_object
        
    def setup(self,assets):
        
        self.create_transition_rules()   
        
        # invoking setup method for each state
        for state in self.states_dict.values():
            
            if (state.key == SubStateMachine.StateKeys.START) or (state.key == SubStateMachine.StateKeys.STOP):
                continue
            else:
                state.setup(assets)
            #endif
        #endfor
        
    def create_transition_rules(self):
        
        self.stand_state = self.StandState(self.game_object)
        self.walk_state = self.WalkState(self.game_object)
        self.unwary_state = self.UnwaryState(self.game_object)
        self.standup_state = StandupState(self.game_object)
        
        # transitions
        self.add_transition(self.start_state, self.ActionKeys.START_SM, self.walk_state.key)
        
        self.add_transition(self.walk_state, BasicState.LA.STEP_GAME, self.unwary_state.key, lambda: self.walk_state.time_consumed)
        self.add_transition(self.walk_state, BasicState.LA.STEP_GAME, self.stand_state.key, lambda: self.walk_state.pause_walk)
        self.add_transition(self.walk_state, BasicState.LA.STEP_GAME, self.stop_state.key, lambda: self.walk_state.player_sighted)
        
        self.add_transition(self.unwary_state, BasicState.LA.STEP_GAME, self.standup_state.key, lambda: self.unwary_state.time_consumed)
        self.add_transition(self.stand_state, BasicState.LA.STEP_GAME, self.walk_state.key, lambda: self.stand_state.time_consumed)
        self.add_transition(self.standup_state,AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED, self.walk_state.key)
        
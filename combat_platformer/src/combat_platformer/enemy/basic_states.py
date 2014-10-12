import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import SubStateMachine
from simple_platformer.game_object import AnimatableObject
from combat_platformer.player.action_keys import PlayerActionKeys
from combat_platformer.level.action_keys import LevelActionKeys
from combat_platformer.enemy import EnemyProperties
from combat_platformer.enemy import EnemyBase

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
    
    
class BasicState(State):
    
    LA = LevelActionKeys
    PA = PlayerActionKeys
    
    
    def __init__(self,key,character):
        
        State.__init__(self,key)
        self.character = character  
        
    def setup(self,assets):
        
        print "setup method for state %s is unimplemented"%(self.key)    


        
class RunState(BasicState):
    
    def __init__(self,character):
        
        BasicState.__init__(self,StateKeys.RUN,self.character)        
        self.speed = 0 
        
    def enter(self):
                 
        self.character.set_current_animation_key(StateKeys.RUN)
        
    def setup(self,assets):
        
        self.speed = self.character.properties.run_speed
        self.add_action(BasicState.LA.STEP_GAME, lambda : self.update())   
        
    def update(self):
        pass
        
class JumpState(BasicState):
    
    def __init__(self,character):
        
        BasicState.__init__(self,StateKeys.JUMP,character)        
              
        self.has_landed = False
                      
        
    def setup(self,asset):
        
        self.speed = self.character.properties.jump_speed 
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update())  
        self.add_action(BasicState.LA.APPLY_GRAVITY,lambda g: self.character.apply_gravity(g))    
        self.add_action(BasicState.LA.COLLISION_ABOVE,lambda platform : self.character.set_vertical_speed(0))
        self.add_action(BasicState.LA.COLLISION_RIGHT_WALL,lambda platform : self.character.set_momentum(0))
        self.add_action(BasicState.LA.COLLISION_LEFT_WALL,lambda platform : self.character.set_momentum(0)) 

    def update(self):
        pass
    
    def enter(self):        
        
        self.character.set_vertical_speed(self.speed)
        self.character.set_current_animation_key(StateKeys.JUMPING)
        self.character.midair_dash_countdown = self.character.properties.max_midair_dashes
        self.character.range_collision_group.add(self.range_sprite) 
        
    def exit(self):
        self.character.range_collision_group.remove(self.range_sprite)      
        self.has_landed = False
        
class DropState(BasicState):
    
    def __init__(self,character):
        BasicState.__init__(self, StateKeys.DROP , character)
                        
        self.add_action(LevelActionKeys.APPLY_GRAVITY,lambda g: self.character.apply_gravity(g))
        self.add_action(AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED,
                lambda : self.character.set_current_animation_key(StateKeys.DROP,[-1]))
        
    def setup(self,asset):
        pass
    
    def enter(self):
            
        self.character.set_current_animation_key(StateKeys.DROP)
        self.character.set_horizontal_speed(0)
        
class WipeoutState(BasicState):
    
    def __init__(self,character):
        
        BasicState.__init__(self, StateKeys.WIPEOUT, character)
        self.time_down = 2000
        self.time_left = 0
        self.time_consumed = False
        self.start_consume_time = False
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))
        self.add_action(AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED,
                lambda : self.animation_expired())
        
    def enter(self):
        self.character.set_current_animation_key(StateKeys.WIPEOUT)
        self.character.set_vertical_speed(0)
        self.time_left = self.time_down
        self.start_consume_time = False
        self.time_consumed = False
        
    def animation_expired(self):
        self.start_consume_time = True
        self.character.set_current_animation_key(StateKeys.WIPEOUT,[-1])
        
    def update(self,time_elapsed):
        
        if self.start_consume_time:
            self.time_left-=time_elapsed
            
            if self.time_left <= 0:
                self.time_consumed = True
            #endif
        #endif
        
class StandupState(BasicState):
    
    def __init__(self,character):
        BasicState.__init__(self, StateKeys.STANDUP, character)
        
    def enter(self):
        self.character.set_current_animation_key(StateKeys.STANDUP)
                  
        
class AlertState(BasicState):
    
    def __init__(self,character):
        BasicState.__init__(self,StateKeys.ALERT,character) 
        
        self.time_active = 10
        self.time_left = 10
        self.time_consumed = False
        self.alert_area_sprite = pygame.sprite.Sprite()
        
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))
        
    def setup(self,assets):
        
        self.time_active = self.character.properties.alert_time
        
        pr = self.character.rect
        self.alert_area_sprite.rect = self.character.properties.sight_area_rect
        self.alert_area_sprite.offset = (0,(pr.height - self.alert_area_sprite.rect.height)/2)
        
    def update(self,time_elapsed):
        
        if self.is_player_in_area():
            
            #reset time
            self.time_left = self.time_active
        else:
            
            self.time_left -= time_elapsed
            
            if self.time_left <= 0:
                self.time_consumed = True
            #endif
        #endif
    
    def is_player_in_area(self):
        
        ps = self.target_player
        ar = self.alert_area_sprite
        cs = self.character
        
        ar.rect.centerx = cs.rect.centerx + ar.offset[0]
        ar.rect.centery = cs.rect.centery + ar.offset[1]
        
        return pygame.sprite.collide_rect(ps, cs)
    
    def enter(self):
        
        self.time_left = self.time_active
        self.time_consumed = False
        
        self.character.set_vertical_speed(0)
        self.character.set_current_animation_key(StateKeys.ALERT)
        
    
class PatrolState(SubStateMachine):
    
    class WalkState(BasicState):
    
        def __init__(self,character):
            
            BasicState.__init__(self,StateKeys.WALK,character)      
              
            self.speed = 0 
            self.patrol_rect = None
            self.time_active = 10000
            self.time_left = 10000
            self.time_consumed = False
            self.player_sighted = False
            
              
            self.sight_sprite = pygame.sprite.Sprite()
            self.range_sprite = pygame.sprite.Sprite()              
            
            self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))    
            self.add_action(BasicState.LA.COLLISION_RIGHT_WALL, lambda platforms : self.turn_around(True))
            self.add_action(BasicState.LA.COLLISION_LEFT_WALL, lambda platforms : self.turn_around(False))
            self.add_action(BasicState.LA.PLAYER_IN_RANGE,
                            lambda player,range_sprites : self.check_player_insight(player,range_sprites))
            
        def enter(self):
            
            print "Entered PATROL WALK state with %s base location"%(str(self.character.rect.bottom))
                     
            self.time_left = self.time_active
            self.time_consumed = False
                    
            self.character.set_current_animation_key(StateKeys.WALK)
            self.character.range_collision_group.add(self.range_sprite)
            self.character.range_collision_group.add(self.sight_sprite)
            self.character.set_horizontal_speed(self.speed)
            
        def exit(self):
            self.character.range_collision_group.remove(self.range_sprite)
            self.character.range_collision_group.remove(self.sight_sprite)
            
            print "Exit PATROL WALK state"
            
        def setup(self,assets):
            
            self.speed = self.character.properties.walk_speed  
            self.patrol_rect  = self.character.properties.patrol_area_rect
            self.time_active = self.character.properties.patrol_walk_time
            
            # sight sprite
            pr = self.character.rect
            self.sight_sprite.rect = pygame.Rect(0,0,300,100) 
            self.sight_sprite.offset = (0,(pr.height - self.sight_sprite.rect.height)/2)
            
            # range sprite
            self.range_height_extension = 4
            self.range_sprite.rect = self.character.rect.copy()
            self.range_sprite.rect.height = self.range_sprite.rect.height + self.range_height_extension
            self.range_sprite.offset = (0,0)
            
        def turn_around(self,collision_right):
            
            if self.character.facing_right == collision_right:
                
                if self.character.facing_right:
                    self.character.turn_left(-self.speed)
                else :
                    self.character.turn_right(self.speed)
                #endif
                
            #endif
            
        def is_inside_patrol_area(self):
            
            ps = self.character
            
            return (ps.rect.left > self.patrol_rect.left) or \
                (ps.rect.right < self.patrol_rect.right)  
                
        def check_player_insight(self,player,range_sprites):
            
            cs = self.character
            ps = player
            for sp in range_sprites:
                
                if sp == self.sight_sprite:                    
                    if self.character.facing_right and (self.rect.centerx < ps.rect.centerx):
                        self.character.target_player = player
                        self.player_sighted = True
                    
                    elif self.character.facing_left and (self.rect.centerx > ps.rect.centerx):
                        self.character.target_player = player
                        self.player_sighted = True
                        
                    #endif
                    
                    break
                
                #endif
            #endfor                   

            
        def update(self,time_elapsed):
                     
            # update time counter
            self.time_left -= time_elapsed
            
            if self.is_inside_patrol_area():
                
                # check active time
                if self.time_left <= 0:
                    self.time_consumed = True
                #endif
                
            else:             
                self.turn_around()
            
            #endif
            
    class UnwaryState(BasicState):
        
        def __init__(self,character):
            
            BasicState.__init__(self,StateKeys.UNWARY,character)
            
            self.time_active = 10000
            self.time_left = 10000 
            self.time_consumed = False
            
            self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))  
            self.add_action(AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED,
                            lambda : self.character.set_current_animation_key(StateKeys.UNWARY,[-1]))
            
        def enter(self):      
            
            self.character.set_current_animation_key(StateKeys.UNWARY)
            self.time_left = self.time_active
            self.time_consumed = False  
            self.character.set_horizontal_speed(0) 
        
        def setup(self,assets):
            
            self.time_active = self.character.properties.patrol_unwary_time
            
        def update(self,time_elapsed):
            
            self.time_left -= time_elapsed
            if self.time_left <= 0:
                
                print 'UNWARY state time consumed, time elapsed %i'%(time_elapsed)
                self.time_consumed = True
            #endif                
    
    
    def __init__(self,parent_sm,character):
        
        SubStateMachine.__init__(self,StateKeys.PATROL ,parent_sm)
        self.character = character
        
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
        
        self.walk_state = self.WalkState(self.character)
        self.unwary_state = self.UnwaryState(self.character)
        self.standup_state = StandupState(self.character)
        
        # transitions
        self.add_transition(self.start_state, self.ActionKeys.START_SM, self.walk_state.key)
        
        self.add_transition(self.walk_state, BasicState.LA.STEP_GAME, self.unwary_state.key, lambda: self.walk_state.time_consumed)
        self.add_transition(self.walk_state, BasicState.LA.STEP_GAME, self.stop_state.key, lambda: self.walk_state.player_sighted)
        
        self.add_transition(self.unwary_state, BasicState.LA.STEP_GAME, self.standup_state.key, lambda: self.unwary_state.time_consumed)
        self.add_transition(self.standup_state,AnimatableObject.ActionKeys.ACTION_SEQUENCE_EXPIRED, self.walk_state.key)
        
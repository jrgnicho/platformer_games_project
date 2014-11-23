from simple_platformer.game_state_machine import *
from simple_platformer.game_object import *
from combat_platformer.player.basic_states import *
from combat_platformer.player.action_keys import *
from combat_platformer.player import PlayerBase
from combat_platformer.level.action_keys import *

class PlayerStateMachine(StateMachine,PlayerBase):
    
    
    def __init__(self):
    
        # superclass constructors
        PlayerBase.__init__(self)
        StateMachine.__init__(self)
        
        # registering handler
        self.add_event_handler(AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED,self,self.action_sequence_expired_handler)
        
        
    def setup(self,assets):
        
        PlayerBase.setup(self,assets)
        self.create_transition_rules()   
        
        # invoking setup method for each state
        for state in self.states_dict.values():
            if not state.setup(assets):
                print "ERROR: state %s setup failed"%(state.key)
                return False
            #endif
        #endfor        
             
        return True
        
    def action_sequence_expired_handler(self):
            self.execute(AnimatableObject.ActionKeys.ANIMATION_SEQUENCE_COMPLETED)
            
            
    def create_transition_rules(self):
        
        run_state = RunState(self)
        dash_state = DashState(self)
        midair_dash_state = MidairDashState(self)
        dash_breaking_state = DashBreakingState(self)
        stand_state = StandState(self)
        stand_edge_state = StandOnEdgeState(self)
        jump_state = JumpState(self)
        fall_state = FallState(self)
        land_state = LandState(self)
        hanging_state = HangingState(self)
        climbing_state = ClimbingState(self)
        
        
        # transitions
        sm = self
        
        sm.add_transition(run_state,PlayerActionKeys.CANCEL_MOVE,StateKeys.STANDING)
        sm.add_transition(run_state,PlayerActionKeys.JUMP,StateKeys.JUMPING)
        sm.add_transition(run_state,LevelActionKeys.PLATFORM_SUPPORT_LOST,StateKeys.FALLING)
        sm.add_transition(run_state,PlayerActionKeys.DASH,StateKeys.DASHING)
        sm.add_transition(run_state,PlayerActionKeys.MOVE_LEFT,StateKeys.DASH_BREAKING,
                          lambda: self.momentum > 0)
        sm.add_transition(run_state,PlayerActionKeys.MOVE_RIGHT,StateKeys.DASH_BREAKING,
                          lambda: self.momentum < 0)
        
        
        sm.add_transition(dash_state,PlayerActionKeys.CANCEL_DASH,StateKeys.DASH_BREAKING,
                          lambda: self.get_animation_progress_percentage()>=0.3)
        sm.add_transition(dash_state,PlayerActionKeys.CANCEL_DASH,StateKeys.RUNNING,
                          lambda: self.get_animation_progress_percentage()<0.3)
        sm.add_transition(dash_state,PlayerActionKeys.JUMP,StateKeys.JUMPING)
        sm.add_transition(dash_state,LevelActionKeys.PLATFORM_SUPPORT_LOST,StateKeys.FALLING)
        sm.add_transition(dash_state,PlayerActionKeys.ANIMATION_SEQUENCE_COMPLETED,StateKeys.RUNNING)
        
        
        sm.add_transition(midair_dash_state,PlayerActionKeys.CANCEL_DASH,StateKeys.FALLING)
        sm.add_transition(midair_dash_state,PlayerActionKeys.ANIMATION_SEQUENCE_COMPLETED,StateKeys.FALLING)
        
        sm.add_transition(dash_breaking_state,PlayerActionKeys.MOVE_LEFT,StateKeys.RUNNING,
                          lambda: not self.facing_right)
        sm.add_transition(dash_breaking_state,PlayerActionKeys.MOVE_RIGHT,StateKeys.RUNNING,
                          lambda: self.facing_right)
        sm.add_transition(dash_breaking_state,PlayerActionKeys.JUMP,StateKeys.JUMPING)
        sm.add_transition(dash_breaking_state,LevelActionKeys.PLATFORM_SUPPORT_LOST,StateKeys.FALLING)
        sm.add_transition(dash_breaking_state,LevelActionKeys.STEP_GAME,StateKeys.STANDING,
                          lambda: self.momentum == 0)
        
        
        sm.add_transition(stand_state,PlayerActionKeys.RUN,StateKeys.RUNNING)
        sm.add_transition(stand_state,PlayerActionKeys.JUMP,StateKeys.JUMPING)
        sm.add_transition(stand_state,LevelActionKeys.PLATFORM_SUPPORT_LOST,StateKeys.FALLING)
        sm.add_transition(stand_state,PlayerActionKeys.MOVE_LEFT,StateKeys.RUNNING)
        sm.add_transition(stand_state,PlayerActionKeys.MOVE_RIGHT,StateKeys.RUNNING)
        sm.add_transition(stand_state,PlayerActionKeys.DASH,StateKeys.DASHING)
        sm.add_transition(stand_state,LevelActionKeys.PLATFORMS_IN_RANGE,StateKeys.STANDING_ON_EDGE,
                          lambda: stand_state.is_standing_on_edge)
        sm.add_transition(stand_state,LevelActionKeys.PLATFORMS_IN_RANGE,StateKeys.FALLING,
                  lambda: stand_state.is_beyond_edge)
        
        
        sm.add_transition(stand_edge_state,PlayerActionKeys.RUN,StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,PlayerActionKeys.JUMP,StateKeys.JUMPING)
        sm.add_transition(stand_edge_state,LevelActionKeys.PLATFORM_SUPPORT_LOST,StateKeys.FALLING)
        sm.add_transition(stand_edge_state,PlayerActionKeys.MOVE_LEFT,StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,PlayerActionKeys.MOVE_RIGHT,StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,PlayerActionKeys.DASH,StateKeys.DASHING)
        
        sm.add_transition(jump_state,PlayerActionKeys.DASH,StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_remaining > 0)
        sm.add_transition(jump_state,PlayerActionKeys.LAND,StateKeys.LANDING)
        sm.add_transition(jump_state,LevelActionKeys.PLATFORM_COLLISION_BELOW,StateKeys.LANDING,
                          lambda : jump_state.has_landed)
        sm.add_transition(jump_state,PlayerActionKeys.ANIMATION_SEQUENCE_COMPLETED,StateKeys.FALLING)
        sm.add_transition(jump_state,LevelActionKeys.PLATFORM_COLLISION_ABOVE,StateKeys.FALLING)
        sm.add_transition(jump_state,LevelActionKeys.PLATFORMS_IN_RANGE,StateKeys.HANGING,
                          lambda : jump_state.edge_in_reach)
        
        sm.add_transition(fall_state,PlayerActionKeys.DASH,StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_remaining > 0)
        sm.add_transition(fall_state,PlayerActionKeys.LAND,StateKeys.LANDING)
        sm.add_transition(fall_state,LevelActionKeys.PLATFORM_COLLISION_BELOW,StateKeys.LANDING,
                          lambda : fall_state.has_landed)
        sm.add_transition(fall_state,LevelActionKeys.PLATFORMS_IN_RANGE,StateKeys.HANGING,
                          lambda : fall_state.edge_in_reach)
        
        sm.add_transition(hanging_state,PlayerActionKeys.JUMP,StateKeys.JUMPING,
                          lambda : self.get_animation_progress_percentage()>0.2) 
        sm.add_transition(hanging_state,PlayerActionKeys.MOVE_UP,StateKeys.CLIMBING,
                          lambda : self.get_animation_progress_percentage()>=1) 
        
        sm.add_transition(climbing_state,PlayerActionKeys.ANIMATION_SEQUENCE_COMPLETED,StateKeys.STANDING) 
        
        
        sm.add_transition(land_state,PlayerActionKeys.ANIMATION_SEQUENCE_COMPLETED,StateKeys.STANDING)  
        sm.add_transition(land_state,PlayerActionKeys.JUMP,StateKeys.JUMPING,
                          lambda : self.get_animation_progress_percentage()>0.2)  
        sm.add_transition(land_state,PlayerActionKeys.DASH,StateKeys.DASHING,
                          lambda : self.get_animation_progress_percentage()>0.2)
        sm.add_transition(land_state,LevelActionKeys.PLATFORM_SUPPORT_LOST,StateKeys.FALLING) 
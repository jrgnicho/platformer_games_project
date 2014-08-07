from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.players import AnimatablePlayer
from simple_platformer.game_state_machine import *

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
        run_state = self.create_base_game_state(PlayerStateMachine.StateKeys.RUNNING,
                                                 AnimatablePlayer.RUN_SPEED, lambda: self.run(), None)
        
        # dash state
        dash_state = State(PlayerStateMachine.StateKeys.DASHING)
        dash_state.set_entry_callback(lambda: (
                                               self.set_current_animation_key(ActionKeys.DASH),
                                               self.set_forward_speed(AnimatablePlayer.DASH_SPEED)))
        
        # dash breaking
        dash_breaking_state = State(PlayerStateMachine.StateKeys.DASH_BREAKING)
        dash_breaking_state.set_entry_callback(lambda: (
                                               self.set_current_animation_key(ActionKeys.DASH_BREAK),
                                               self.set_forward_speed(AnimatablePlayer.DASH_BREAKING_SPEED)))
        
        # stand state
        stand_state = self.create_base_game_state(PlayerStateMachine.StateKeys.STANDING,
                                                 0, lambda: self.stand(), None)
        
        # stand edge state
        stand_edge_state = self.create_base_game_state(PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                                                 0, None, None)
        stand_edge_state.set_entry_callback(lambda: (
                                       self.set_current_animation_key(ActionKeys.STAND_EDGE),
                                       self.set_forward_speed(0)))
        stand_edge_state.add_action(ActionKeys.ACTION_SEQUENCE_EXPIRED,
                                    lambda : self.set_current_animation_key(ActionKeys.STAND_EDGE,[-1])) #last frame
        
        # jump state
        jump_state = self.create_base_game_state(PlayerStateMachine.StateKeys.JUMPING,
                                         AnimatablePlayer.RUN_SPEED, lambda: self.jump(), None)
        jump_state.add_action(ActionKeys.CANCEL_MOVE,lambda : self.cancel_move())
        jump_state.add_action(ActionKeys.CANCEL_JUMP,lambda : self.cancel_jump())
        jump_state.add_action(ActionKeys.APPLY_GRAVITY,lambda : self.apply_gravity())
        
        # fall state
        fall_state = self.create_base_game_state(PlayerStateMachine.StateKeys.FALLING,
                                 AnimatablePlayer.RUN_SPEED, lambda: self.fall(), None)
        fall_state.add_action(ActionKeys.CANCEL_MOVE,lambda : self.cancel_move())
        fall_state.add_action(ActionKeys.APPLY_GRAVITY,lambda : self.apply_gravity())
        
        # land state
        land_state = State(PlayerStateMachine.StateKeys.LANDING)
        land_state.set_entry_callback(lambda : self.land())        

        
        # transitions
        sm = self
        
        sm.add_transition(run_state,ActionKeys.STAND,PlayerStateMachine.StateKeys.STANDING)
        sm.add_transition(run_state,ActionKeys.CANCEL_MOVE,PlayerStateMachine.StateKeys.STANDING)
        sm.add_transition(run_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(run_state,ActionKeys.FALL,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(run_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(run_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING)
        
        sm.add_transition(dash_state,ActionKeys.STAND,PlayerStateMachine.StateKeys.DASH_BREAKING)
        #sm.add_transition(dash_state,ActionKeys.CANCEL_DASH,PlayerStateMachine.StateKeys.DASH_BREAKING,
        #                  lambda: self.animation_set_progress_percentage()>=0.4)
        #sm.add_transition(dash_state,ActionKeys.CANCEL_DASH,PlayerStateMachine.StateKeys.RUNNING,
        #                  lambda: self.animation_set_progress_percentage()<0.4)
        sm.add_transition(dash_state,ActionKeys.CANCEL_DASH,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(dash_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(dash_state,ActionKeys.FALL,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(dash_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: self.facing_right)
        sm.add_transition(dash_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: (not self.facing_right))
        
        #sm.add_transition(dash_state,ActionKeys.STAND,PlayerStateMachine.StateKeys.STANDING)
        sm.add_transition(dash_breaking_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(dash_breaking_state,ActionKeys.FALL,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_breaking_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_breaking_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.STANDING)
        #sm.add_transition(dash_breaking_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING,
        #                  lambda: not self.facing_right)
        #sm.add_transition(dash_breaking_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING,
        #                  lambda: (self.facing_right))
        
        sm.add_transition(stand_state,ActionKeys.RUN,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(stand_state,ActionKeys.FALL,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING)
        sm.add_transition(stand_state,ActionKeys.LEFT_EDGE_NEAR,PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                          lambda: not self.facing_right)
        sm.add_transition(stand_state,ActionKeys.RIGHT_EDGE_NEAR,PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                          lambda: self.facing_right)
        
        sm.add_transition(stand_edge_state,ActionKeys.RUN,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(stand_edge_state,ActionKeys.FALL,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_edge_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_edge_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING)
        
        sm.add_transition(jump_state,ActionKeys.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(jump_state,ActionKeys.FALL,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(jump_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_ABOVE,PlayerStateMachine.StateKeys.FALLING)
        
        sm.add_transition(fall_state,ActionKeys.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(fall_state,ActionKeys.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING)
        
        sm.add_transition(land_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.STANDING)  
        sm.add_transition(land_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING,
                          lambda : self.animation_set_progress_percentage()>0.2)  
        sm.add_transition(land_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING,
                          lambda : self.animation_set_progress_percentage()>0.2)
        sm.add_transition(land_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING) 
        
        
        
    def create_base_game_state(self,state_key,move_speed,entry_cb = None,exit_cb = None):
        
        state = State(state_key)
        state.set_entry_callback(entry_cb)
        state.set_exit_callback(exit_cb)
        
        state.add_action(ActionKeys.MOVE_LEFT,lambda : self.turn_left(-move_speed))
        state.add_action(ActionKeys.MOVE_RIGHT,lambda : self.turn_right(move_speed))
        #state.add_action(ActionKeys.STEP_GAME,lambda : True)
        
        
        return state
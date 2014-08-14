from simple_platformer.animatable_object import AnimatableObject
from simple_platformer.players import AnimatablePlayer
from simple_platformer.players import PlayerProperties
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
        HANGING = "HANGING"
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
        def run_entry():
            self.run()
            self.player_properties.max_x_position_change = self.player_properties.run_speed
            
        def run_exit():
            self.player_properties.max_x_position_change = self.player_properties.dash_speed 
        
        run_state = self.create_base_game_state(PlayerStateMachine.StateKeys.RUNNING,
                                                 self.player_properties.run_speed, run_entry,run_exit)
        
        
        # dash state
        dash_state = State(PlayerStateMachine.StateKeys.DASHING)
        dash_state.set_entry_callback(lambda: self.dash())
        dash_state.set_exit_callback(lambda: self.set_inertia(0.8*self.player_properties.dash_speed 
                                                              if self.animation_set_progress_percentage()>0.3 else 0))
        
        # dash state
        midair_dash_state = State(PlayerStateMachine.StateKeys.MIDAIR_DASHING)
        midair_dash_state.set_exit_callback(lambda: self.set_inertia(self.player_properties.dash_speed * 
                                                                     self.animation_set_progress_percentage()))
        midair_dash_state.set_entry_callback(lambda: self.midair_dash())
        #midair_dash_state.set_exit_callback(lambda: self.set_inertia(self.player_properties.dash_speed if 
        #                                                             self.animation_set_progress_percentage()>0.2 else
        #                                                             0.5*self.player_properties.dash_speed))
        
        # dash breaking 
        dash_breaking_state = State(PlayerStateMachine.StateKeys.DASH_BREAKING)
        dash_breaking_state.set_entry_callback(lambda:self.dash_break( self.player_properties.run_speed))
        dash_breaking_state.set_exit_callback(lambda: self.set_inertia(0))
        dash_breaking_state.add_action(ActionKeys.ACTION_SEQUENCE_EXPIRED,
                                    lambda : self.set_current_animation_key(ActionKeys.DASH_BREAK,[-1])) #last frame
        
        
        # stand state
        def stand_entry():
            self.stand()
            self.set_inertia(0)
        
        stand_state = State(PlayerStateMachine.StateKeys.STANDING)
        stand_state.set_entry_callback(stand_entry)
        
        
        
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
                                         self.player_properties.run_speed, lambda: self.jump(), None)
        jump_state.add_action(ActionKeys.CANCEL_MOVE,lambda : self.set_forward_speed(0))
        jump_state.add_action(ActionKeys.CANCEL_JUMP,lambda : self.cancel_jump())
        jump_state.add_action(ActionKeys.APPLY_GRAVITY,lambda g: self.apply_gravity(g))    
        jump_state.add_action(ActionKeys.COLLISION_RIGHT_WALL,lambda left: self.set_inertia(0))
        jump_state.add_action(ActionKeys.COLLISION_LEFT_WALL,lambda right: self.set_inertia(0)) 
        
        
        # fall state
        class FallState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.FALLING)
                
                self.player = player
                
                self.add_action(ActionKeys.CANCEL_MOVE,
                                lambda : self.player.set_forward_speed(0))
                self.add_action(ActionKeys.APPLY_GRAVITY,lambda g: self.player.apply_gravity(g))
                self.add_action(ActionKeys.MOVE_LEFT,lambda : self.player.turn_left(-self.player.player_properties.run_speed))
                self.add_action(ActionKeys.MOVE_RIGHT,lambda : self.player.turn_right(self.player.player_properties.run_speed))
                self.add_action(ActionKeys.COLLISION_RIGHT_WALL,lambda left: self.player.set_inertia(0))
                self.add_action(ActionKeys.COLLISION_LEFT_WALL,lambda right: self.player.set_inertia(0))
            
            def enter(self):
                
                self.player.fall()
                
        fall_state = FallState(self)
        
        # land state
        land_state = State(PlayerStateMachine.StateKeys.LANDING)
        land_state.set_entry_callback(lambda : self.land())     
        
        # hanging state
        class HangingState(State):
            
            def __init__(self,player):
                
                State.__init__(self,PlayerStateMachine.StateKeys.HANGING)
                
                self.player = player
                self.plaform_rect = None
                
                self.add_action(ActionKeys.LEFT_EDGE_NEAR,self.cling_to_rect)
                self.add_action(ActionKeys.RIGHT_EDGE_NEAR,self.cling_to_rect)
                self.add_action(ActionKeys.ACTION_SEQUENCE_EXPIRED,
                                    lambda : self.player.set_current_animation_key(ActionKeys.HANG,[-1])) 
                
                
            def cling_to_rect(self,rect = None):
                
                if self.plaform_rect != rect:
                    self.plaform_rect = rect
                    
                    if self.player.facing_right:
                        self.player.collision_sprite.rect.right = self.plaform_rect.left - self.player.player_properties.hang_distance_from_side
                    else:
                        self.player.collision_sprite.rect.left = self.plaform_rect.right + self.player.player_properties.hang_distance_from_side
                    
                    #endif
                        
                    self.player.collision_sprite.rect.top = self.plaform_rect.top + self.player.player_properties.hang_distance_from_top
                    
                print "Hanging at top point %i"%(self.player.collision_sprite.rect.top)
                
            def enter(self):
                self.player.set_current_animation_key(ActionKeys.HANG)
                self.player.set_forward_speed(0)
                self.player.set_upward_speed(0)
                self.player.set_inertia(0)
                
            def exit(self):
                self.plaform_rect = None
        
        hanging_state = HangingState(self)
                
                    

        
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
                          lambda: self.animation_set_progress_percentage()>0.2)
        sm.add_transition(dash_state,ActionKeys.CANCEL_DASH,PlayerStateMachine.StateKeys.RUNNING,
                          lambda: not (self.animation_set_progress_percentage()>0.2))
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
        sm.add_transition(stand_state,ActionKeys.LEFT_EDGE_NEAR,PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                          lambda: not self.facing_right)
        sm.add_transition(stand_state,ActionKeys.RIGHT_EDGE_NEAR,PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                          lambda: self.facing_right)
        
        
        sm.add_transition(stand_edge_state,ActionKeys.RUN,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(stand_edge_state,ActionKeys.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_edge_state,ActionKeys.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.DASHING)
        
        sm.add_transition(jump_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_countdown > 0)
        sm.add_transition(jump_state,ActionKeys.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(jump_state,ActionKeys.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.COLLISION_ABOVE,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,ActionKeys.RIGHT_EDGE_NEAR,PlayerStateMachine.StateKeys.HANGING,
                          lambda: (not self.facing_right) and (self.current_upward_speed > 0))
        sm.add_transition(jump_state,ActionKeys.LEFT_EDGE_NEAR,PlayerStateMachine.StateKeys.HANGING,
                          lambda: self.facing_right and (self.current_upward_speed > 0))
        
        sm.add_transition(fall_state,ActionKeys.DASH,PlayerStateMachine.StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_countdown > 0)
        sm.add_transition(fall_state,ActionKeys.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(fall_state,ActionKeys.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(fall_state,ActionKeys.RIGHT_EDGE_NEAR,PlayerStateMachine.StateKeys.HANGING,lambda: not self.facing_right)
        sm.add_transition(fall_state,ActionKeys.LEFT_EDGE_NEAR,PlayerStateMachine.StateKeys.HANGING,lambda: self.facing_right)
        
        sm.add_transition(hanging_state,ActionKeys.JUMP,PlayerStateMachine.StateKeys.JUMPING,
                          lambda : self.animation_set_progress_percentage()>0.2) 
        
        
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
        
        return state
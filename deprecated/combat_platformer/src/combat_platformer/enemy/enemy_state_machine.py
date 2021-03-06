from simple_platformer.game_state_machine import *
from simple_platformer.game_object import *
from combat_platformer.level.action_keys import *
from combat_platformer.enemy import EnemyBase
from combat_platformer.enemy import EnemyProperties
from combat_platformer.enemy.basic_states import *

class EnemyStateMachine(StateMachine,EnemyBase):
    
    def __init__(self):
        
        # superclass constructors
        StateMachine.__init__(self)
        EnemyBase.__init__(self)
        
        # registering handler
        self.add_event_handler(AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED,self,
                               self.action_sequence_expired_handler)
        
        # states
        self.patrol_state = None
        self.alert_state = None
        
    def setup(self, assets):
        
        EnemyBase.setup(self)
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
        
        self.patrol_state = PatrolState(self)
        self.alert_state = AlertState(self)
        self.drop_state = DropState(self)
        self.wipeout_state = WipeoutState(self)    
        self.standup_state = StandupState(self)   

        
        self.add_transition(self.patrol_state,StateMachineActionKeys.SUBMACHINE_STOP,
                            self.alert_state.key)
        self.add_transition(self.patrol_state,LevelActionKeys.PLATFORM_SUPPORT_LOST,self.drop_state.key)
        
        self.add_transition(self.drop_state,LevelActionKeys.PLATFORM_COLLISION_BELOW,self.wipeout_state.key)
        
        self.add_transition(self.wipeout_state,LevelActionKeys.STEP_GAME,self.standup_state.key,
                            lambda: self.wipeout_state.time_consumed)
        
        self.add_transition(self.standup_state,AnimatableObject.ActionKeys.ANIMATION_SEQUENCE_COMPLETED, self.patrol_state.key)
        
        
        self.add_transition(self.alert_state,LevelActionKeys.STEP_GAME,self.patrol_state.key,lambda: self.alert_state.time_consumed)
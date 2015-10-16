from physics_platformer.state_machine import Action
from physics_platformer.state_machine import State
from physics_platformer.state_machine import StateMachine
from physics_platformer.state_machine import StateEvent
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.game_actions import *
from physics_platformer.character.character_states import *
from physics_platformer.src.physics_platformer.character.character_states import CharacterStateKeys,\
  StandingState, RunningState, TakeoffState, JumpState, FallState

class CharacterStateMachine(StateMachine):
  
  def __init__(self,character_object,states_dict = None):
    StateMachine.__init__(self)
    self.character_obj_ = character_object
    self.states_dict_ = states_dict
    self.supported_states_ = [CharacterStateKeys.STANDING.key, 
                              CharacterStateKeys.RUNNING.key,
                              CharacterStateKeys.TAKEOFF.key,
                              CharacterStateKeys.JUMPING.key,
                              CharacterStateKeys.FALLING.key,
                              CharacterStateKeys.LANDING.key]
    
  def setup(self):
    
    if not self.setupStates():
      return False
    
    self.setupTransitionRules()
  
  def setupStates(self):
    if self.states_dict_ is not None:
      
      for k in self.supported_states_:
        if not self.states_dict_.has_key(k):
          return False
    
    else:
      
      # creating default states
      standing_state = StandingState(self.character_obj_, self)
      running_state = RunningState(self.character_obj_,self)
      takeoff_state = TakeoffState(self.character_obj_,self)
      jump_state = JumpState(self.character_obj_,self)
      fall_state = FallState(self.character_obj_,self)
      land_state = LandState(self.character_obj_,self)
      
      self.states_dict_[standing_state.key] = standing_state
      self.states_dict_[running_state.key] = running_state
      self.states_dict_[takeoff_state.key] = takeoff_state
      self.states_dict_[jump_state.key] = jump_state
      self.states_dict_[fall_state.key] = fall_state
      self.states_dict_[land_state.key] = land_state
    
    return True
  
  def setupTransitionRules(self):
    
    self.addState(self.states_dict_[CharacterStateKeys.STANDING.key])
    self.addState(self.states_dict_[CharacterStateKeys.RUNNING.key])
    self.addState(self.states_dict_[CharacterStateKeys.TAKEOFF.key])
    self.addState(self.states_dict_[CharacterStateKeys.JUMPING.key])
    self.addState(self.states_dict_[CharacterStateKeys.FALLING.key])
    self.addState(self.states_dict_[CharacterStateKeys.LANDING.key])
    
    return True
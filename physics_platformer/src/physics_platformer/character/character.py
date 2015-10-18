from physics_platformer.game_objects import CharacterObject
from physics_plaformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import *
from physics_platformer.state_machine import Action
from physics_platformer.state_machine import State
from physics_platformer.state_machine import StateMachine
from physics_platformer.state_machine import StateEvent
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.game_actions import *
from physics_plaformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import CharacterStates

class Character(CharacterObject):
  
  def __init__(self,character_info):
    CharacterObject.__init__(self.character_info)
    
    self.controller_sm_ = StateMachine()    
    
  def setup(self):    

    self.__setupDefaultStates__()
    self.__setupTransitionRules__()
    
    return True
    
  def execute(self,action):
    self.controller_sm_.execute(action)
    
  def __setupDefaultStates__(self):
    
    # creating default states
    standing_state = CharacterStates.StandingState(self, self.controller_sm_)
    running_state = CharacterStates.RunningState(self,self.controller_sm_)
    takeoff_state = CharacterStates.TakeoffState(self,self.controller_sm_)
    jump_state = CharacterStates.JumpState(self,self.controller_sm_)
    fall_state = CharacterStates.FallState(self,self.controller_sm_)
    land_state = CharacterStates.LandState(self,self.controller_sm_)
    
    self.controller_sm_.addState(standing_state.key)
    self.controller_sm_.addState(running_state.key)
    self.controller_sm_.addState(takeoff_state.key)
    self.controller_sm_.addState(jump_state.key)
    self.controller_sm_.addState(fall_state.key)
    self.controller_sm_.addState(land_state.key)
    
    
  def __setupTransitionRules__(self):    
    
    self.controller_sm_.addTransition(CharacterStateKeys.STANDING,CharacterAction.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.controller_sm_.addTransition(CharacterStateKeys.STANDING,CharacterAction.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.controller_sm_.addTransition(CharacterStateKeys.STANDING,CharacterAction.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.controller_sm_.addTransition(CharacterStateKeys.STANDING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    
    self.controller_sm_.addTransition(CharacterStateKeys.RUNNING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    self.controller_sm_.addTransition(CharacterStateKeys.RUNNING,CharacterAction.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.controller_sm_.addTransition(CharacterStateKeys.RUNNING,CharacterAction.MOVE_NONE.key,CharacterStateKeys.STANDING)
    
    self.controller_sm_.addTransition(CharacterStateKeys.TAKEOFF, StateMachineActions.DONE.key, CharacterStateKeys.JUMPING)
    self.controller_sm_.addTransition(CharacterStateKeys.JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.controller_sm_.addTransition(CharacterStateKeys.FALLING, CollisionAction.SURFACE_COLLISION, CharacterStateKeys.LANDING)
    self.controller_sm_.addTransition(CharacterStateKeys.LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    
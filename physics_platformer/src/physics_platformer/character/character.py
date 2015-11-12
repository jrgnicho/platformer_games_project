from physics_platformer.game_object import CharacterObject
from physics_platformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import *
from physics_platformer.state_machine import Action
from physics_platformer.state_machine import State
from physics_platformer.state_machine import StateMachine
from physics_platformer.state_machine import StateEvent
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.game_actions import *
from physics_platformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import CharacterStates

class Character(CharacterObject):
  
  def __init__(self,character_info):
    CharacterObject.__init__(self,character_info)
    
    self.sm_ = StateMachine()    
    
  def setup(self):    

    self.__setupDefaultStates__()
    self.__setupTransitionRules__()
    
    return True
    
  def execute(self,action):
    self.sm_.execute(action)
    
  def __setupDefaultStates__(self):
    
    # creating default states
    standing_state = CharacterStates.StandingState(self, self.sm_)
    running_state = CharacterStates.RunningState(self,self.sm_)
    takeoff_state = CharacterStates.TakeoffState(self,self.sm_)
    jump_state = CharacterStates.JumpState(self,self.sm_)
    fall_state = CharacterStates.FallState(self,self.sm_)
    land_state = CharacterStates.LandState(self,self.sm_)
        
    self.sm_.addState(fall_state)
    self.sm_.addState(standing_state)
    self.sm_.addState(running_state)
    self.sm_.addState(takeoff_state)
    self.sm_.addState(jump_state)
    self.sm_.addState(land_state)    
    
  def __setupTransitionRules__(self):    
    
    self.sm_.addTransition(CharacterStateKeys.FALLING, CollisionAction.SURFACE_COLLISION, CharacterStateKeys.LANDING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.MOVE_NONE.key,CharacterStateKeys.STANDING)
    
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, StateMachineActions.DONE.key, CharacterStateKeys.JUMPING)
    self.sm_.addTransition(CharacterStateKeys.JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    
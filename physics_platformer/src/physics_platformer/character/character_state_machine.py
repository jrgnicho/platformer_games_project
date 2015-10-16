from physics_platformer.state_machine import Action
from physics_platformer.state_machine import State
from physics_platformer.state_machine import StateMachine
from physics_platformer.state_machine import StateEvent
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.game_actions import *
from physics_plaformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import *


class CharacterStateMachine(StateMachine):
  
  def __init__(self):
    StateMachine.__init__(self)
    
  def setup(self):  
    
    self.setupTransitionRules()
    return True
  
  def setupTransitionRules(self):    
    
    self.addTransition(CharacterStateKeys.STANDING,CharacterAction.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.addTransition(CharacterStateKeys.STANDING,CharacterAction.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.addTransition(CharacterStateKeys.STANDING,CharacterAction.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.addTransition(CharacterStateKeys.STANDING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    
    self.addTransition(CharacterStateKeys.RUNNING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    self.addTransition(CharacterStateKeys.RUNNING,CharacterAction.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.addTransition(CharacterStateKeys.RUNNING,CharacterAction.MOVE_NONE.key,CharacterStateKeys.STANDING)
    
    self.addTransition(CharacterStateKeys.TAKEOFF, StateMachineActions.DONE.key, CharacterStateKeys.JUMPING)
    self.addTransition(CharacterStateKeys.JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.addTransition(CharacterStateKeys.FALLING, CollisionAction.SURFACE_COLLISION, CharacterStateKeys.LANDING)
    self.addTransition(CharacterStateKeys.LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    
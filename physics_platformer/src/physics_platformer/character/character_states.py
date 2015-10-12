from physics_platformer.state_machine import *
from physics_platformer.game_actions import GeneralActions
from panda3d.core import LVector3

class CharacterState(State):
  
  def __init__(self,key, character_obj, parent_state_machine, animation_key = None):
    """
    CharacterState(string key,CharacterObject character_obj, StateMachine parent_state_machine)
    """
    
    State.__init__(self,key)
    self.character_obj_ = character_obj
    self.parent_state_machine_ = parent_state_machine
    self.animation_key_ = animation_key if (animation_key is not None) else key
    
  def getParentStateMachine(self):
    return self.parent_state_machine_

class CharacterStateKeys(object):
  
  NONE="NONE"
  STANDING="STANDING"
  RETREAT_FROM_LEDGE = "RETREAT_FROM_LEDGE"
  STANDING_ON_LEDGE="STANDING_ON_LEDGE"
  RUNNING="RUNNING"
  TAKEOFF = "TAKEOFF"
  JUMPING="JUMPING"
  FALLING="FALLING"
  LANDING="LANDING"
  DASHING= "DASHING"
  DASH_BREAKING= "DASH_BREAKING"
  MIDAIR_DASHING = "MIDAIR_DASHING"
  CATCH_LEDGE = "CATCHING_LEDGE"
  HANGING = "HANGING"
  CLIMBING = "CLIMBING"
  EXIT = "EXIT"


class StandingState(CharacterState):
  
  def __init__(self,character_obj, parent_state_machine):
    
    CharacterState.__init__(self, CharacterStateKeys.STANDING, character_obj, parent_state_machine)
    
  def enter(self):
    self.character_obj_.play(self.animation_key_)
    
    direction = 1
    direction = direction if self.character_obj_.isFacingRight() else -direction    
    self.character_obj_.setLinearVelocity(LVector3(direction,0,0))
  
  
class RunningState(CharacterState):
  
  def __init__(self,character_obj,parent_state_machine):
    CharacterState.__init__(self, CharacterStateKeys.RUNNING, character_obj, parent_state_machine)
    
  
    
    
    
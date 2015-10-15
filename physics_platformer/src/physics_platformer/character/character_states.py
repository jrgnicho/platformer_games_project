from physics_platformer.state_machine import *
from physics_platformer.game_actions import GeneralActions
from physics_platformer.game_actions import AnimationActions
from physics_platformer.game_actions import CharacterActions
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
    self.character_obj_.setLinearVelocity(LVector3(0,0,0))
  
  
class RunningState(CharacterState):
  
  def __init__(self,character_obj,parent_state_machine):
    CharacterState.__init__(self, CharacterStateKeys.RUNNING, character_obj, parent_state_machine)
    self.forward_speed_ = self.character_obj_.character_info_.run_speed
    self.forward_direction_ = LVector3(self.forward_speed_,0,0)
    
    
    self.addAction(CharacterActions.MOVE_RIGHT.key,self.turnRight)
    self.addAction(CharacterActions.MOVE_LEFT.key,self.turnLeft)  
    self.addAction(GeneralActions.GAME_STEP.key,self.moveUpdate)  
    
  def enter(self):
    self.character_obj_.play(self.animation_key_)   
    
    
  def turnRight(self):   
    if not self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(True)
      
    self.forward_speed_ = abs(self.forward_speed_)
    self.forward_direction_.setX(self.forward_speed_)
    
  def turnLeft(self):
    if self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(False)
      
    self.forward_speed_ = -abs(self.forward_speed_)
    self.forward_direction_.setX(self.forward_speed_)
    
  def moveUpdate(self):
    if self.forward_speed_ > 0:
      self.turnRight()
    else:
      self.turnLeft()
    
class TakeoffState(CharacterState):
  
  def __init__(self,character_obj,parent_state_machine):
    CharacterState.__init__(self, CharacterStateKeys.TAKEOFF, character_obj, parent_state_machine)
    
  def enter(self):
    self.character_obj_.setAnimationEndCallback(self.done)
    
  def done(self):
    action = AnimationActions.ANIMATION_COMPLETED
    self.parent_state_machine_.execute(action)
  
  def exit(self):
    speed_up = self.character_obj_.character_info_.jump_force
    self.character_obj_.setLinearVelocity(LVector3(0,0,speed_up))
      
class JumpState(CharacterState):
  
  def __init__(self,character_obj,parent_state_machine):
    CharacterState.__init__(self, CharacterStateKeys.JUMPING, character_obj, parent_state_machine)
    self.forward_speed_ = self.character_obj_.character_info_.jump_forward
    self.forward_direction_ = LVector3(self.forward_speed_,0,0)
      
    self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
    self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft)
    self.addAction(GeneralActions.GAME_STEP,self.checkAscendFinished)    
    
  def enter(self):
    vel = self.character_obj_.getLinearVelocity()
    
    if abs(vel.getX()) > self.forward_speed_:
      self.forward_speed_ = abs(vel.getX())
      
    vel.setZ(self.character_obj_.character_info_.jump_force)
    self.character_obj_.setLinearVelocity(vel)
      
  def moveRight(self):   
    if not self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(True)
      
    self.forward_direction_.setX(self.forward_speed_)
    self.character_obj_.setLinearVelocity(self.forward_direction_)
    
  def moveLeft(self):
    if self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(False)
      
    self.forward_direction_.setX(-self.forward_speed_)
    self.character_obj_.setLinearVelocity(self.forward_direction_)
    
  def checkAscendFinished(self):
    
    vel = self.character_obj_.getLinearVelocity()
    if vel.getZ() < 0.01:
      vel.setZ(0)
      self.character_obj_.setLinearVelocity(vel)
      self.parent_state_machine_.execute(CharacterActions.FALL)
      
    
    
    
  
    
    
    
from physics_platformer.state_machine import *
from physics_platformer.game_actions import GeneralAction
from physics_platformer.game_actions import AnimationActions
from physics_platformer.game_actions import CharacterActions
from panda3d.core import LVector3

class CharacterStateKeys(object):
  
  NONE="NONE"
  STANDING="STANDING"
  RETREAT_FROM_LEDGE = "RETREAT_FROM_LEDGE"
  STANDING_ON_LEDGE="STANDING_ON_LEDGE"
  RUNNING="RUNNING"
  TAKEOFF = "TAKEOFF"
  JUMPING="JUMPING"
  FALLING="FALL"
  LANDING="LAND"
  DASHING= "DASHING"
  DASH_BREAKING= "DASH_BREAKING"
  MIDAIR_DASHING = "MIDAIR_DASHING"
  CATCH_LEDGE = "CATCHING_LEDGE"
  HANGING = "HANGING"
  CLIMBING = "CLIMBING"
  EXIT = "EXIT"

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
  
  def done(self):
    '''
    done()
      Used by the State when its task(s) is finished
    '''
    StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))
  
  
class CharacterStates(object): # Class Namespace
  
  class StandingState(CharacterState):
    
    def __init__(self,character_obj, parent_state_machine):
      
      CharacterState.__init__(self, CharacterStateKeys.STANDING, character_obj, parent_state_machine)
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.loop(self.animation_key_)    
      self.character_obj_.node().setLinearVelocity(LVector3(0,0,0))
      
    def exit(self):
      self.character_obj_.stop()
    
    
  class RunningState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine):
      CharacterState.__init__(self, CharacterStateKeys.RUNNING, character_obj, parent_state_machine)
      self.forward_speed_ = self.character_obj_.character_info_.run_speed
      self.forward_direction_ = LVector3(self.forward_speed_,0,0)
      
      
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.turnRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.turnLeft)  
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.loop(self.animation_key_)   
      
    def exit(self):
      self.character_obj_.stop()
      
      
    def turnRight(self):   
      if not self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(True)
        
      self.forward_speed_ = abs(self.forward_speed_)
      self.forward_direction_.setX(self.forward_speed_)
      self.character_obj_.node().setLinearVelocity(self.forward_direction_)
      
    def turnLeft(self):
      if self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(False)
        
      self.forward_speed_ = -abs(self.forward_speed_)
      self.forward_direction_.setX(self.forward_speed_)
      self.character_obj_.node().setLinearVelocity(self.forward_direction_)

      
  class TakeoffState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine):
      CharacterState.__init__(self, CharacterStateKeys.TAKEOFF, character_obj, parent_state_machine)
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.play(self.animation_key_)
          
    def exit(self):
      speed_up = self.character_obj_.character_info_.jump_force
      self.character_obj_.node().setLinearVelocity(LVector3(0,0,speed_up))
      self.character_obj_.stop()
      self.character_obj_.setAnimationEndCallback(None)
        
  class JumpState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine):
      CharacterState.__init__(self, CharacterStateKeys.JUMPING, character_obj, parent_state_machine)
      self.forward_speed_ = self.character_obj_.character_info_.jump_forward
        
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft)
      self.addAction(GeneralAction.GAME_STEP,self.checkAscendFinished)    
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      vel = self.character_obj_.node().getLinearVelocity()
      
      if abs(vel.getX()) > self.forward_speed_:
        self.forward_speed_ = abs(vel.getX())
      else:
        self.forward_speed_ = self.character_obj_.character_info_.jump_forward
        
      vel.setZ(self.character_obj_.character_info_.jump_force)
      self.character_obj_.node().setLinearVelocity(vel)
      
      self.character_obj_.loop(self.animation_key_)
      
    def exit(self):
      vel = self.character_obj_.node().getLinearVelocity()
      vel.setZ(0)
      self.character_obj_.node().setLinearVelocity(vel)
      self.character_obj_.stop()    
        
    def moveRight(self):   
      if not self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(True)
        
      vel = self.character_obj_.node().getLinearVelocity()
      vel.setX(self.forward_speed_)    
      self.character_obj_.node().setLinearVelocity(vel)
      
    def moveLeft(self):
      if self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(False)
        
      vel = self.character_obj_.node().getLinearVelocity()
      vel.setX(-self.forward_speed_)    
      self.character_obj_.node().setLinearVelocity(vel)
      
    def checkAscendFinished(self):
      
      vel = self.character_obj_.node().getLinearVelocity()
      if vel.getZ() < 0.01:
        StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))
        
  class FallState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine):
      CharacterState.__init__(self, CharacterStateKeys.FALLING, character_obj, parent_state_machine)
      
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft)
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.loop(self.animation_key_)
      
    def exit(self):
      self.character_obj_.stop()
      
    def moveRight(self):   
      if not self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(True)
        
      vel = self.character_obj_.getLinearVelocity()
      vel.setX(self.forward_speed_)    
      self.character_obj_.node().setLinearVelocity(vel)
      
    def moveLeft(self):
      if self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(False)
        
      vel = self.character_obj_.getLinearVelocity()
      vel.setX(-self.forward_speed_)    
      self.character_obj_.node().setLinearVelocity(vel)
      
  class LandState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine):
      CharacterState.__init__(self, CharacterStateKeys.LANDING, character_obj, parent_state_machine)
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.setAnimationEndCallback(self.done)
      vel = self.character_obj_.node().getLinearVelocity()
      vel.setZ(0)
      self.character_obj_.node().setLinearVelocity(vel)
      self.character_obj_.node().setLinearFactor(LVector3(1,0,0)) # prevent movement in z
      self.character_obj_.play(self.animation_key_)    

      
    def exit(self):
      
      self.character_obj_.node().setLinearFactor(LVector3(1,0,1)) # re-enable movement in z
      self.character_obj_.stop()
      self.character_obj_.setAnimationEndCallback(None)
      
      
      
        
      
      
      
    
      
      
    
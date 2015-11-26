from physics_platformer.state_machine import *
from physics_platformer.game_object import GameObject
from physics_platformer.animation import AnimationActor
from physics_platformer.game_actions import GeneralActions
from physics_platformer.game_actions import AnimationActions
from physics_platformer.game_actions import CharacterActions
from physics_platformer.game_actions import CollisionAction
from physics_platformer.character import CharacterStatus
from panda3d.core import LVector3
from panda3d.core import Vec3
import logging

class CharacterStateKeys(object):
  
  NONE="NONE"
  STANDING="STANDING"
  RETREAT_FROM_LEDGE = "RETREAT_FROM_LEDGE"
  STANDING_NEAR_EDGE="STANDING_NEAR_EDGE"
  STANDING_EDGE_RECOVERY = "STANDING_EDGE_RECOVERY"
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

class CharacterState(State):
  
  def __init__(self,key, character_obj, parent_state_machine, animation_key = None):
    """
    CharacterState(string key,CharacterBase character_obj, StateMachine parent_state_machine)
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
    
class AerialBaseState(CharacterState):
  
  LANDING_THRESHOLD = AnimationActor.BOUND_PADDING
  MIN_WALL_DISTANCE = AnimationActor.BOUND_PADDING 
  
  def __init__(self,key,character_obj,parent_state_machine, animation_key = None):
    CharacterState.__init__(self, key, character_obj, parent_state_machine, animation_key)
    self.forward_speed_ = self.character_obj_.character_info_.jump_forward
    
    self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
    self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft)
    
  def enter(self):
    
    logging.debug("%s state entered"%(self.getKey()))
    
    vel = self.character_obj_.getLinearVelocity()     
    if abs(vel.getX()) > self.character_obj_.character_info_.jump_forward:
      self.forward_speed_ = abs(vel.getX())
    else:
      self.forward_speed_ = self.character_obj_.character_info_.jump_forward  
      
    self.character_obj_.loop(self.animation_key_)
    
  def exit(self):
    self.character_obj_.stop()
    
  def moveRight(self,action):   
    if not self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(True)
      
    vel = self.character_obj_.node().getLinearVelocity()
    vel.setX(self.forward_speed_)    
    self.character_obj_.setLinearVelocity(vel)
    
  def moveLeft(self,action):
    if self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(False)
      
    vel = self.character_obj_.node().getLinearVelocity()
    vel.setX(-self.forward_speed_)    
    self.character_obj_.setLinearVelocity(vel)
  
  # TODO:   Remove method below if not used again for improving behavior around platform edges
  def pushRightFromWall(self,action):
    platform  = action.game_obj2      
    if abs(self.character_obj_.getBottom() - platform.getTop()) < AerialBaseState.LANDING_THRESHOLD :
      return
          
    d = -float("inf")
    use_second = action.contact_manifold.getNode0().getPythonTag(GameObject.ID_PYTHON_TAG) != self.character_obj_.getName()
    for cp in action.contact_manifold.getManifoldPoints():
      cx = cp.getPositionWorldOnB().getX() if use_second else cp.getPositionWorldOnA().getX()
      d = cx if (cx > d) else d        

    self.forward_speed_ = self.character_obj_.character_info_.jump_forward
    if d == -float("inf"):
      logging.warn("No contact points were found")
      return 
    
    self.character_obj_.clampLeft( d + AerialBaseState.MIN_WALL_DISTANCE)
    
  # TODO:   Remove method below if not used again for improving behavior around platform edges
  def pushLeftFromWall(self,action):
    platform  = action.game_obj2      
    if abs(self.character_obj_.getBottom() - platform.getTop()) < AerialBaseState.LANDING_THRESHOLD :
      return
    
    d = float("inf")
    use_second = action.contact_manifold.getNode0().getPythonTag(GameObject.ID_PYTHON_TAG) != self.character_obj_.getName()
    for cp in action.contact_manifold.getManifoldPoints():
      cx = cp.getPositionWorldOnB().getX() if use_second else cp.getPositionWorldOnA().getX()
      d = cx if (cx < d) else d 
    
    self.forward_speed_ = self.character_obj_.character_info_.jump_forward  
    if d == float("inf"):
      logging.warn("No contact points were found")
      return 
      
    self.character_obj_.clampRight( d - AerialBaseState.MIN_WALL_DISTANCE)
      
  
class CharacterStates(object): # Class Namespace
  
  EDGE_PUSH_DISTANCE = 2*AnimationActor.BOUND_PADDING
    
  class StandingState(CharacterState):        
    
    def __init__(self,character_obj, parent_state_machine,animation_key = None):
      
      CharacterState.__init__(self, CharacterStateKeys.STANDING, character_obj, parent_state_machine, animation_key) 
      
      self.addAction(CollisionAction.ACTION_BODY_COLLISION,self.nearEdgeCallback)     
      
    def enter(self):      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.loop(self.animation_key_)    
      platform  = self.character_obj_.getStatus().platform
      self.character_obj_.clampBottom(platform.getMax().getZ())      
      self.character_obj_.node().setLinearFactor(LVector3(1,0,0)) # disable movement in z
      self.character_obj_.setLinearVelocity(LVector3(0,0,0))
      self.character_obj_.clearForces()      
      #self.character_obj_.setRigidBodyActive(False, True)
      
    def exit(self):
      self.character_obj_.stop()
      self.character_obj_.node().setLinearFactor(LVector3(1,0,1))
      #self.character_obj_.setRigidBodyActive(True, True)   
      
    def nearEdgeCallback(self,collision_action):
            
      platform = self.character_obj_.getStatus().platform
      recovery_dist = self.character_obj_.getInfo().edge_recovery_distance
      drop_dist = self.character_obj_.getInfo().edge_drop_distance
      
      # check if truly standing near either edge
      if not (self.character_obj_.getRight() > platform.getRight() or self.character_obj_.getLeft() < platform.getLeft()) :
        return
      
      # determining distance to platform edge
      near_right_edge = self.character_obj_.getRight() > platform.getRight()       
      d = (self.character_obj_.getRight() - platform.getRight()) if near_right_edge else (platform.getLeft() - self.character_obj_.getLeft())
      
      facing_oposite = near_right_edge == self.character_obj_.isFacingRight()
      
      # storing relevant variables
      self.character_obj_.getStatus().contact_data = CharacterStatus.ContactData(self.character_obj_.getName(),bottom = collision_action.contact_manifold)
      self.character_obj_.getStatus().platform = platform
      
      # recover move request
      if d > recovery_dist and d < drop_dist:        
        StateMachine.postEvent(StateEvent(self.parent_state_machine_, CharacterActions.EDGE_RECOVERY))
      
      # fall from the platform  
      if d >= drop_dist:        
        logging.debug("Pushing character out of platform")
        if near_right_edge:
          self.character_obj_.clampLeft(platform.getRight() + CharacterStates.EDGE_PUSH_DISTANCE)
        else:
          self.character_obj_.clampRight(platform.getLeft() - CharacterStates.EDGE_PUSH_DISTANCE)
      
  class StandingEdgeRecovery(CharacterState):
    
    def __init__(self,character_obj, parent_state_machine,animation_key = None):   
      CharacterState.__init__(self, CharacterStateKeys.STANDING_EDGE_RECOVERY, character_obj, parent_state_machine, animation_key)  
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))
      
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.pose(self.animation_key_)
      
      # determining x position
      xoffset = 0
      facing_right = self.character_obj_.isFacingRight() 
      if self.character_obj_.getAnimatorActor().getActionGhostBody() is not None:
        node = self.character_obj_.getAnimatorActor().getActionGhostBody().node()
        xoffset = node.getShapePos(0).getX()
        xoffset = xoffset if facing_right else -xoffset
      
      platform  = self.character_obj_.getStatus().platform  
      last_contact = self.character_obj_.getStatus().contact_data
      pos_x = platform.getRight() if facing_right else platform.getLeft()
      pos_x -= xoffset
      self.character_obj_.setX(pos_x)        
      self.character_obj_.play(self.animation_key_)
      
    def exit(self):
      self.character_obj_.setAnimationEndCallback(None)
      self.character_obj_.stop()
        
  class StandingNearEdge(CharacterState):
    def __init__(self,character_obj, parent_state_machine,animation_key = None):   
      CharacterState.__init__(self, CharacterStateKeys.STANDING_NEAR_EDGE, character_obj, parent_state_machine, animation_key) 
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))              
      self.character_obj_.loop(self.animation_key_)  
      
    def exit(self):
      self.character_obj_.stop()
    
  class RunningState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.RUNNING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.run_speed
      self.forward_direction_ = LVector3(self.forward_speed_,0,0)      
      
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.turnRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.turnLeft)  
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.loop(self.animation_key_)   
      
    def exit(self):      
      self.character_obj_.stop()       
      
    def turnRight(self,action):   
      if not self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(True)
        
      self.forward_speed_ = abs(self.forward_speed_)
      self.forward_direction_ = self.character_obj_.node().getLinearVelocity()
      self.forward_direction_.setX(self.forward_speed_)
      self.character_obj_.setLinearVelocity(self.forward_direction_)
      
    def turnLeft(self,action):
      if self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(False)
        
      self.forward_speed_ = -abs(self.forward_speed_)
      self.forward_direction_ = self.character_obj_.node().getLinearVelocity()
      self.forward_direction_.setX(self.forward_speed_)
      self.character_obj_.setLinearVelocity(self.forward_direction_)

      
  class TakeoffState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.TAKEOFF, character_obj, parent_state_machine, animation_key)     
      
      self.forward_speed_ = self.character_obj_.character_info_.jump_forward
      
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft)
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
            
      # setting z+ speed
      vel = self.character_obj_.node().getLinearVelocity()
      
      # storing x speed  
      if abs(vel.getX()) - self.character_obj_.character_info_.jump_forward > 0:
        self.forward_speed_ = abs(vel.getX())
      else:
        self.forward_speed_ = self.character_obj_.character_info_.jump_forward  
          
      vel.setZ(self.character_obj_.character_info_.jump_force)
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.play(self.animation_key_)
      self.character_obj_.applyCentralImpulse(LVector3(0,0,self.character_obj_.character_info_.jump_force))
      
    def moveRight(self,action):   
      if not self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(True)
        
      vel = self.character_obj_.node().getLinearVelocity()
      vel.setX(self.forward_speed_)    
      self.character_obj_.setLinearVelocity(vel)
      
    def moveLeft(self,action):
      if self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(False)
        
      vel = self.character_obj_.node().getLinearVelocity()
      vel.setX(-self.forward_speed_)    
      self.character_obj_.setLinearVelocity(vel)
          
    def exit(self):
      self.character_obj_.enableFriction(False)
      self.character_obj_.stop()
      self.character_obj_.setAnimationEndCallback(None)
        
  class JumpState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.JUMPING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.jump_forward
        
      self.addAction(GeneralActions.GAME_STEP,self.checkAscendFinished)    
        
    def exit(self):
      vel = self.character_obj_.node().getLinearVelocity()
      vel.setZ(0)
      self.character_obj_.setLinearVelocity(vel)
      self.character_obj_.stop()           

      
    def checkAscendFinished(self,action):
      
      vel = self.character_obj_.node().getLinearVelocity()
      if vel.getZ() < 0.01:
        StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))
        
  class FallState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.FALLING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.jump_forward
      
      self.addAction(CollisionAction.SURFACE_COLLISION,self.verifyLanding)

    def verifyLanding(self,action):
      
      platform  = action.game_obj2
      if abs(self.character_obj_.getBottom() - platform.getTop()) < AerialBaseState.LANDING_THRESHOLD :
        self.character_obj_.getStatus().platform = platform
        StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))
       
      
  class LandState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.LANDING, character_obj, parent_state_machine, animation_key)
      self.clamped_ = False
      
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.play(self.animation_key_)  
      self.clampToPlatform(self.character_obj_.getStatus().platform)
      self.character_obj_.enableFriction(True)
      
    def clampToPlatform(self,platform):
      
      self.character_obj_.clampBottom(platform.getMax().getZ())      
      self.character_obj_.node().setLinearFactor(LVector3(1,0,0)) # disable movement in z
      
    def exit(self):      
      self.character_obj_.node().setLinearFactor(LVector3(1,0,1)) # re-enable movement in z
      self.character_obj_.stop()
      self.character_obj_.setAnimationEndCallback(None)
      
      
      
        
      
      
      
    
      
      
    
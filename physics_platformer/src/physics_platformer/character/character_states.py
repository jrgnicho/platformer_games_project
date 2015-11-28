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
  EDGE_LANDING = "EDGE_LANDING"
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
        
  def ceilingCollisionCallback(self,action): 
    platform   = action.game_obj2
    manifold = action.contact_manifold
    contact_data = CharacterStatus.ContactData(self.character_obj_.getName(), bottom = manifold)
    pz = contact_data.points_bottom.on_collided[0].getZ()
    
    logging.debug("clamping to top")
    self.character_obj_.clampTop(pz - CharacterStates.EDGE_PUSH_DISTANCE)
    self.character_obj_.clearForces()
    StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))
  
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
      recovery_min = self.character_obj_.getInfo().fall_recovery_min
      recovery_max = self.character_obj_.getInfo().fall_recovery_max
      
      # check if truly standing near either edge
      if not (self.character_obj_.getRight() > platform.getRight() or self.character_obj_.getLeft() < platform.getLeft()) :
        return
      
      # determining distance to platform edge
      near_right_edge = self.character_obj_.getRight() > platform.getRight()       
      d = (self.character_obj_.getRight() - platform.getRight()) if near_right_edge else (platform.getLeft() - self.character_obj_.getLeft())
      
      facing_oposite = near_right_edge != self.character_obj_.isFacingRight()
      
      # storing relevant variables
      self.character_obj_.getStatus().contact_data = CharacterStatus.ContactData(self.character_obj_.getName(),bottom = collision_action.contact_manifold)
      self.character_obj_.getStatus().platform = platform
      
      # push from the platform  
      if d >= recovery_max:        
        logging.debug("Pushing character out of platform")
        if near_right_edge:
          self.character_obj_.clampLeft(platform.getRight() + CharacterStates.EDGE_PUSH_DISTANCE)
        else:
          self.character_obj_.clampRight(platform.getLeft() - CharacterStates.EDGE_PUSH_DISTANCE)

      if d > recovery_min and d < recovery_max and not facing_oposite:      
          StateMachine.postEvent(StateEvent(self.parent_state_machine_, CharacterActions.EDGE_RECOVERY))      

      
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
      self.character_obj_.clampOriginX(pos_x)         
      self.character_obj_.play(self.animation_key_)  
      
    def exit(self):
      self.character_obj_.setAnimationEndCallback(None)
      self.character_obj_.stop()
        
  class StandingNearEdge(CharacterState):
    def __init__(self,character_obj, parent_state_machine,animation_key = None):   
      CharacterState.__init__(self, CharacterStateKeys.STANDING_NEAR_EDGE, character_obj, parent_state_machine, animation_key) 
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))      
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
      self.character_obj_.clampOriginX(pos_x)   
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

      
  class TakeoffState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.TAKEOFF, character_obj, parent_state_machine, animation_key)     
      
      self.forward_speed_ = self.character_obj_.character_info_.jump_forward
      
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft)
      self.addAction(CollisionAction.CEILING_COLLISION,self.ceilingCollisionCallback) 
      
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
          
    def exit(self):
      self.character_obj_.enableFriction(False)
      self.character_obj_.stop()
      self.character_obj_.setAnimationEndCallback(None)
        
  class JumpState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.JUMPING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.jump_forward
        
      self.addAction(GeneralActions.GAME_STEP,self.checkAscendFinished)    
      self.addAction(CollisionAction.CEILING_COLLISION,self.ceilingCollisionCallback) 
        
    def exit(self):
      vel = self.character_obj_.getLinearVelocity()
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
      
      self.addAction(CollisionAction.SURFACE_COLLISION,self.surfaceCollisionCallback)
      
    def enter(self):
      AerialBaseState.enter(self)
      
      vel = self.character_obj_.getLinearVelocity()
      if vel.getZ() > 0:
        vel.setZ(0)
        self.character_obj_.setLinearVelocity(vel)
        

    def surfaceCollisionCallback(self,action):
      
      platform  = action.game_obj2
      if abs(self.character_obj_.getBottom() - platform.getTop()) < AerialBaseState.LANDING_THRESHOLD :
        self.character_obj_.getStatus().platform = platform
        self.character_obj_.getStatus().contact_data = CharacterStatus.ContactData(action.contact_manifold)
        
        near_edge = ( self.character_obj_.getLeft() < platform.getLeft() or self.character_obj_.getRight() > platform.getRight())
        facing_away = True
        if near_edge:
          facing_away = self.character_obj_.getFront() < platform.getLeft() or self.character_obj_.getFront() > platform.getRight()
        
        if not facing_away:  
          info = self.character_obj_.getInfo()
          d = abs(self.character_obj_.getFront() - platform.getLeft()) if self.character_obj_.isFacingRight() else abs(self.character_obj_.getFront() - platform.getRight())
          
          if d > info.land_edge_min and d < info.land_edge_max:
            StateMachine.postEvent(StateEvent(self.parent_state_machine_, CharacterActions.LAND_EDGE))
          
          if d < info.land_edge_min:
            # push out of platform
            if self.character_obj_.isFacingRight():
              self.character_obj_.clampRight(platform.getLeft()-CharacterStates.EDGE_PUSH_DISTANCE)
            else:
              self.character_obj_.clampLeft(platform.getRight()+CharacterStates.EDGE_PUSH_DISTANCE)
          if d > info.land_edge_max:
            StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))
            
        else:
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
      
  class EdgeLandingState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.EDGE_LANDING, character_obj, parent_state_machine, animation_key)
      self.clamped_ = False
      
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.play(self.animation_key_)  
      
      # placing character  on platform      
      platform = self.character_obj_.getStatus().platform
      self.clampToPlatform(platform)      
      if self.character_obj_.isFacingRight():
        self.character_obj_.clampLeft(platform.getLeft())
      else:
        self.character_obj_.clampRight(platform.getRight())        
      
      self.character_obj_.enableFriction(True)
      
    def clampToPlatform(self,platform):
      
      self.character_obj_.clampBottom(platform.getMax().getZ())      
      self.character_obj_.node().setLinearFactor(LVector3(1,0,0)) # disable movement in z
      
    def exit(self):      
      self.character_obj_.node().setLinearFactor(LVector3(1,0,1)) # re-enable movement in z
      self.character_obj_.stop()
      self.character_obj_.setAnimationEndCallback(None)
      
      
      
        
      
      
      
    
      
      
    
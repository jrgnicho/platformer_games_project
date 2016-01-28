from physics_platformer.state_machine import *
from physics_platformer.game_object import GameObject
from physics_platformer.animation import AnimationActor
from physics_platformer.game_actions import GeneralActions
from physics_platformer.game_actions import AnimationActions
from physics_platformer.game_actions import CharacterActions
from physics_platformer.game_actions import CollisionAction
from physics_platformer.character import CharacterStatus
from physics_platformer.collision import CollisionMasks
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func
from panda3d.core import LVector3, LMatrix4
from panda3d.core import Vec3
from panda3d.core import TransformState
import logging
import inspect

class CharacterStateKeys(object):
  
  NONE="NONE"
  STANDING="STANDING"
  RETREAT_FROM_LEDGE = "RETREAT_FROM_LEDGE"
  STANDING_NEAR_EDGE="STANDING_NEAR_EDGE"
  STANDING_EDGE_RECOVERY = "STANDING_EDGE_RECOVERY"
  RUNNING="RUNNING"
  TAKEOFF = "TAKEOFF"
  JUMPING="JUMPING"
  AIR_JUMPING = "AIR_JUMPING"
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
  
  def clampToPlatform(self):
    
    result = self.character_obj_.doCollisionSweepTestZ()
    if result.hasHit():
      self.character_obj_.clampBottom(result.getHitPos().getZ())
    else:  
      platform = self.character_obj_.getStatus().platform
      self.character_obj_.clampBottom(platform.getMax().getZ())      
    
    self.character_obj_.node().setLinearFactor(LVector3(1,0,0)) # disable movement in z
  
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
    self.forward_speed_ = self.character_obj_.character_info_.jump_fwd_speed
    self.current_speed_ = 0
    self.move_exec_seq_ = None
    
    self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
    self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft)
    self.addAction(CharacterActions.MOVE_NONE.key,self.moveStop)
    
  def enter(self):
    
    logging.debug("%s state entered"%(self.getKey()))
    
    # store forward speed
    momentum_x = self.character_obj_.getStatus().momentum.getX()  
    if abs(momentum_x) > self.character_obj_.character_info_.jump_fwd_speed:
      self.forward_speed_ = abs(momentum_x)* self.character_obj_.character_info_.jump_momentum
    else:
      self.forward_speed_ = self.character_obj_.character_info_.jump_fwd_speed  
      
    self.character_obj_.animate(self.animation_key_)          
    self.move_exec_seq_ = Sequence()
    finterv = Func(self.moveForwardCallback)
    self.move_exec_seq_.append(finterv)
    self.move_exec_seq_.loop()
    
  def exit(self):      
    self.character_obj_.stop() 
    if self.move_exec_seq_ is not None: 
      self.move_exec_seq_.finish()
      self.move_exec_seq_ = None     
    
  def moveForwardCallback(self):
    
    self.forward_direction_ = self.character_obj_.node().getLinearVelocity()
    self.forward_direction_.setX(self.current_speed_)
    self.character_obj_.setLinearVelocity(self.forward_direction_)
    
  def moveStop(self,action):    
    self.current_speed_ = 0
    
  def moveRight(self,action):    
    if not self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(True)
      
    self.current_speed_ = abs(self.forward_speed_)
    
  def moveLeft(self,action):
    if self.character_obj_.isFacingRight():
      self.character_obj_.faceRight(False)
      
    self.current_speed_ = -abs(self.forward_speed_)   
    
  def ceilingCollisionCallback(self, action):
    vel = self.character_obj_.getLinearVelocity()
    if vel.getZ() < 0:
      vel.setZ(0)
      self.character_obj_.setLinearVelocity(vel)
      StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))
      
  def checkAscendFinished(self,action):
    
    vel = self.character_obj_.node().getLinearVelocity()
    if vel.getZ() < 0.01:
      StateMachine.postEvent(StateEvent(self.parent_state_machine_, StateMachineActions.DONE))  
          
class CharacterStates(object): # Class Namespace
  
  EDGE_PUSH_DISTANCE = 2*AnimationActor.BOUND_PADDING
    
  class StandingState(CharacterState):        
    
    def __init__(self,character_obj, parent_state_machine,animation_key = None):
      
      CharacterState.__init__(self, CharacterStateKeys.STANDING, character_obj, parent_state_machine, animation_key) 
      
      self.addAction(CollisionAction.LEDGE_COLLISION,self.ledgeCollisionCallback)     
      
    def enter(self):      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.animate(self.animation_key_)    
      self.character_obj_.node().setLinearFactor(LVector3(1,0,0)) # disable movement in z
      self.character_obj_.setLinearVelocity(LVector3(0,0,0))
      self.character_obj_.clearForces()      
      
    def exit(self):
      self.character_obj_.stop()
      self.character_obj_.node().setLinearFactor(LVector3(1,0,1))
      self.character_obj_.getStatus().momentum.setX(0)
      
    def ledgeCollisionCallback(self,collision_action):
            
      ledge  = collision_action.game_obj2
      recovery_min = self.character_obj_.getInfo().fall_recovery_min
      recovery_max = self.character_obj_.getInfo().fall_recovery_max
      
      d = abs(self.character_obj_.getFront() - ledge.getX(self.character_obj_.getParent()))

        
      if self.character_obj_.isFacingRight() == ledge.isRightSideLedge():        
        # push from the platform  
        if d >= recovery_max:        
          logging.debug("Pushing character out of platform")
          if self.character_obj_.isFacingRight():
            self.character_obj_.clampLeft(ledge.getX(self.character_obj_.getParent()) + CharacterStates.EDGE_PUSH_DISTANCE)
          else:
            self.character_obj_.clampRight(ledge.getX(self.character_obj_.getParent()) - CharacterStates.EDGE_PUSH_DISTANCE)
  
        if d > recovery_min and d < recovery_max :      
            StateMachine.postEvent(StateEvent(self.parent_state_machine_, CharacterActions.EDGE_RECOVERY)) 
          
      # storing relevant variables
      self.character_obj_.getStatus().contact_data = CharacterStatus.ContactData(self.character_obj_.getName(),bottom = collision_action.contact_manifold)
      self.character_obj_.getStatus().platform = ledge.getParentPlatform()      
      self.character_obj_.getStatus().ledge = ledge     

      
  class StandingEdgeRecovery(CharacterState):
    
    def __init__(self,character_obj, parent_state_machine,animation_key = None):   
      CharacterState.__init__(self, CharacterStateKeys.STANDING_EDGE_RECOVERY, character_obj, parent_state_machine, animation_key)  
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))
      
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.pose(self.animation_key_)
      
      # determining x position of ghost body
      xoffset = 0
      facing_right = self.character_obj_.isFacingRight() 
      if self.character_obj_.getAnimatorActor().getActionGhostBody() is not None:
        node = self.character_obj_.getAnimatorActor().getActionGhostBody().node()
        xoffset = node.getShapePos(0).getX()
        xoffset = xoffset if facing_right else -xoffset
        
      ledge =  self.character_obj_.getStatus().ledge       
      self.character_obj_.clampOriginX(ledge.getX(self.character_obj_.getParent()) - xoffset)
      self.character_obj_.clampBottom(ledge.getZ(self.character_obj_.getParent()) )
      self.character_obj_.animate(self.animation_key_)  
      
    def exit(self):
      self.character_obj_.setAnimationEndCallback(None)
      self.character_obj_.stop()
      self.character_obj_.getStatus().momentum.setX(0)
        
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
      self.character_obj_.animate(self.animation_key_)
      
    def exit(self):
      self.character_obj_.stop()
      self.character_obj_.getStatus().momentum.setX(0)
    
  class RunningState(CharacterState):
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.RUNNING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.run_speed
      self.forward_direction_ = LVector3(self.forward_speed_,0,0)   
      self.move_exec_seq_   = None
      
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.turnRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.turnLeft)   
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.animate(self.animation_key_)  
      
      self.forward_speed_ = 0       
      self.move_exec_seq_ = Sequence()
      finterv = Func(self.moveForwardCallback)
      self.move_exec_seq_.append(finterv)
      self.move_exec_seq_.loop()
      
    def exit(self):      
      self.character_obj_.stop()  
      self.move_exec_seq_.finish()
      self.move_exec_seq_ = None     
      self.character_obj_.getStatus().momentum.setX(self.character_obj_.character_info_.run_speed)
      
    def moveForwardCallback(self):
      
      self.forward_direction_ = self.character_obj_.node().getLinearVelocity()
      self.forward_direction_.setX(self.forward_speed_)
      self.character_obj_.setLinearVelocity(self.forward_direction_)
      
    def turnRight(self,action):   
      if not self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(True)
        
      self.forward_speed_ = self.character_obj_.character_info_.run_speed
      
    def turnLeft(self,action):
      if self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(False)
        
      self.forward_speed_ = -self.character_obj_.character_info_.run_speed
      
      
  class DashState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.DASHING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = abs(self.character_obj_.character_info_.dash_speed)
      self.forward_direction_ = LVector3(self.forward_speed_,0,0)   
      self.move_exec_seq_   = None
      self.falling_ = False
      
      self.addAction(CollisionAction.FREE_FALL,self.freeFallCallback) 
      self.addAction(CollisionAction.SURFACE_COLLISION,self.surfaceCollisionCallback)
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.setAnimationEndCallback(self.animationEndCallback)
      self.character_obj_.animate(self.animation_key_)  
      
      self.forward_speed_ = abs(self.character_obj_.character_info_.dash_speed)
      if self.character_obj_.isFacingRight():
        self.forward_speed_ = abs(self.forward_speed_)
      else:
        self.forward_speed_ = -abs(self.forward_speed_)
      
      self.move_exec_seq_ = Sequence()
      finterv = Func(self.moveForwardCallback)
      self.move_exec_seq_.append(finterv)
      self.move_exec_seq_.loop()
      
    def exit(self):      
      self.character_obj_.stop()        
      self.character_obj_.setAnimationEndCallback(None)
      self.move_exec_seq_.finish()
      self.move_exec_seq_ = None     
      self.character_obj_.getStatus().momentum.setX(self.character_obj_.character_info_.dash_speed)
      
    def surfaceCollisionCallback(self,action):
      self.falling_ = False
      
    def freeFallCallback(self,action):
      self.falling_ = True
      
    def animationEndCallback(self):
      
      if self.falling_:
        StateMachine.postEvent(StateEvent(self.parent_state_machine_, CharacterActions.FALL))
      else:
        self.done()
      
    def moveForwardCallback(self):
      
      self.forward_direction_ = self.character_obj_.node().getLinearVelocity()
      self.forward_direction_.setX(self.forward_speed_)
      self.character_obj_.setLinearVelocity(self.forward_direction_)     
      
  class MidairDashState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.MIDAIR_DASHING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = abs(self.character_obj_.character_info_.dash_speed)
      self.forward_direction_ = LVector3(self.forward_speed_,0,0)   
      self.move_exec_seq_   = None
      self.falling_ = True
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.animate(self.animation_key_)  
      
      self.forward_speed_ = abs(self.character_obj_.character_info_.dash_speed)
      if self.character_obj_.isFacingRight():
        self.forward_speed_ = abs(self.forward_speed_)
      else:
        self.forward_speed_ = -abs(self.forward_speed_)
      
      self.move_exec_seq_ = Sequence()
      finterv = Func(self.moveForwardCallback)
      self.move_exec_seq_.append(finterv)
      self.move_exec_seq_.loop()
      
      self.character_obj_.getStatus().air_dashes_count+=1
      
    def exit(self):      
      self.character_obj_.stop()        
      self.character_obj_.setAnimationEndCallback(None)
      self.move_exec_seq_.finish()
      self.move_exec_seq_ = None     
      self.character_obj_.getStatus().momentum.setX(self.character_obj_.character_info_.dash_speed)
      
    def moveForwardCallback(self):
      
      self.forward_direction_ = self.character_obj_.node().getLinearVelocity()
      self.forward_direction_.setX(self.forward_speed_)
      self.forward_direction_.setZ(0)
      self.character_obj_.setLinearVelocity(self.forward_direction_)           
      
  class TakeoffState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.TAKEOFF, character_obj, parent_state_machine, animation_key)   
      
    def enter(self):      
      logging.debug("%s state entered"%(self.getKey()))
                  
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.animate(self.animation_key_)
                
    def exit(self):
      AerialBaseState.exit(self)
      self.character_obj_.enableFriction(False)
      self.character_obj_.setAnimationEndCallback(None)
        
  class JumpState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.JUMPING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.jump_fwd_speed
      
      self.addAction(GeneralActions.GAME_STEP,self.checkAscendFinished)
      self.addAction(CollisionAction.CEILING_COLLISION,self.ceilingCollisionCallback)  
      
    def enter(self):
      AerialBaseState.enter(self)
      self.character_obj_.applyCentralImpulse(LVector3(0,0,self.character_obj_.character_info_.jump_force))
              
    def exit(self):
      
      AerialBaseState.exit(self)
      vel = self.character_obj_.getLinearVelocity()
      vel.setZ(0)
      self.character_obj_.setLinearVelocity(vel)
      
        
  class AirJumpState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.AIR_JUMPING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.jump_fwd_speed
        
      self.addAction(GeneralActions.GAME_STEP,self.checkAscendFinished)  
      self.addAction(CollisionAction.CEILING_COLLISION,self.ceilingCollisionCallback)  
      
    def enter(self):
      
      vel = self.character_obj_.getLinearVelocity()
      vel.setZ(0)
      self.character_obj_.setLinearVelocity(vel)
      self.character_obj_.applyCentralImpulse(LVector3(0,0,self.character_obj_.character_info_.airjump_force))      
      self.character_obj_.getStatus().air_jumps_count+=1
      AerialBaseState.enter(self) 
        
    def exit(self):
      
      AerialBaseState.exit(self)
      vel = self.character_obj_.getLinearVelocity()
      vel.setZ(0)
      self.character_obj_.setLinearVelocity(vel)
      
  class CatchLedgeState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine,animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.CATCH_LEDGE, character_obj, parent_state_machine, animation_key)
      
      self.addAction(CollisionAction.LEDGE_COLLISION,self.ledgeCollisionCallback)
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.moveRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.moveLeft) 
      self.addAction(CharacterActions.MOVE_NONE.key,self.moveNone) 
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))
      
      self.character_obj_.animate(self.animation_key_) 
      self.character_obj_.getStatus().air_jumps_count = 0
      self.character_obj_.getStatus().air_dashes_count = 0
      
    def moveNone(self,action):   
      self.character_obj_.getStatus().momentum.setX(0)   
      
    def moveRight(self,action):   
      self.character_obj_.getStatus().momentum.setX(self.character_obj_.character_info_.run_speed)
      
    def moveLeft(self,action):
      self.character_obj_.getStatus().momentum.setX(self.character_obj_.character_info_.run_speed)
      
    def ledgeCollisionCallback(self,action):

      ledge = action.game_obj2
      ghost_body = self.character_obj_.getActionGhostBody()
      self.character_obj_.getStatus().platform = ledge.getParentPlatform()
      self.character_obj_.getStatus().ledge = ledge
            
      self.character_obj_.setStatic(True)
      
      # detemining position of ghost action body relative to character
      pos = ghost_body.node().getShapePos(0)
      if not self.character_obj_.isFacingRight(): # rotate about z by 180 if looking left
        pos.setX(-pos.getX())
      
      # creating transform  for placement of character relative to ledge
      tf_obj_to_ghost = LMatrix4.translateMat(pos)        
      tf_ghost_to_object = LMatrix4(tf_obj_to_ghost)
      tf_ghost_to_object.invertInPlace()
      tf_world_to_ledge = ledge.getMat(self.character_obj_.getParent())      
      transform = TransformState.makeMat(tf_world_to_ledge * tf_ghost_to_object)
      
      # placing character on ledge
      pos = Vec3(transform.getPos().getX(),0,transform.getPos().getZ())
      self.character_obj_.setPos(pos)
      self.character_obj_.setLinearVelocity(Vec3(0,0,0))        
      
      # turning off collision
      ghost_body.node().setIntoCollideMask(CollisionMasks.NO_COLLISION)
      
      logging.debug(inspect.stack()[0][3] + ' invoked')
      
    def exit(self): 
      
      self.character_obj_.getActionGhostBody().node().setIntoCollideMask(CollisionMasks.ACTION_BODY)   
      self.character_obj_.setStatic(False)
      self.character_obj_.stop()
      
  class ClimbingState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine,animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.CLIMBING, character_obj, parent_state_machine, animation_key)
      
    def enter(self):
      logging.debug("%s state entered"%(self.getKey()))
      
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.animate(self.animation_key_)
      
      self.clampToPlatformEdge()
      
    def clampToPlatformEdge(self):
      platform = self.character_obj_.getStatus().platform
      ledge = self.character_obj_.getStatus().ledge

      self.character_obj_.clampBottom(ledge.getZ(self.character_obj_.getParent()))
      self.character_obj_.clampBack(ledge.getX(self.character_obj_.getParent()))
      self.character_obj_.setLinearVelocity(Vec3(0,0,0))   
      
    def exit(self):
      
      self.character_obj_.stop()      
      self.character_obj_.setAnimationEndCallback(None)
      
    def climb(self):
      pass
        
  class FallState(AerialBaseState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      AerialBaseState.__init__(self, CharacterStateKeys.FALLING, character_obj, parent_state_machine, animation_key)
      self.forward_speed_ = self.character_obj_.character_info_.jump_fwd_speed      
      
      self.addAction(CollisionAction.SURFACE_COLLISION,self.surfaceCollisionCallback)
      self.addAction(GeneralActions.GAME_STEP,self.capFallSpeed)      
      
    def enter(self):
      self.character_obj_.enableFriction(False)
      AerialBaseState.enter(self)
      
      vel = self.character_obj_.getLinearVelocity()
      if vel.getZ() > 0:
        vel.setZ(0)
        self.character_obj_.setLinearVelocity(vel)
                
    def capFallSpeed(self,action):
        
        vel = self.character_obj_.getLinearVelocity()
        if vel.getZ() < self.character_obj_.character_info_.fall_max_speed:
            vel.setZ(self.character_obj_.character_info_.fall_max_speed)
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
            
            if self.character_obj_.isFacingRight():
              # push out of platform
              self.character_obj_.clampRight(platform.getLeft()-CharacterStates.EDGE_PUSH_DISTANCE)
            else:
              # pull into platform
              self.character_obj_.clampLeft(platform.getRight()+CharacterStates.EDGE_PUSH_DISTANCE)
          if d > info.land_edge_max:
            StateMachine.postEvent(StateEvent(self.parent_state_machine_, CharacterActions.LAND))
            
        else:
          StateMachine.postEvent(StateEvent(self.parent_state_machine_, CharacterActions.LAND))
     
  class LandState(CharacterState):
    
    def __init__(self,character_obj,parent_state_machine, animation_key = None):
      CharacterState.__init__(self, CharacterStateKeys.LANDING, character_obj, parent_state_machine, animation_key)
      self.clamped_ = False      
      
      self.addAction(CharacterActions.MOVE_RIGHT.key,self.turnRight)
      self.addAction(CharacterActions.MOVE_LEFT.key,self.turnLeft) 
      self.addAction(CharacterActions.MOVE_NONE.key,self.turnNone) 
      
    def enter(self):
      
      logging.debug("%s state entered"%(self.getKey()))
      self.character_obj_.setAnimationEndCallback(self.done)
      self.character_obj_.animate(self.animation_key_)  
      
      self.clampToPlatform()   
      
      self.character_obj_.enableFriction(True)
      self.character_obj_.getStatus().air_jumps_count = 0
      self.character_obj_.getStatus().air_dashes_count = 0
      self.character_obj_.getStatus().momentum.setX(0)
      
    def surfaceCollisionCallback(self,action):
      '''
      Performs a collision sweep in order to determine the height at which the character comes into contact
      with the landing surface
      '''
      
      physics_world = self.character_obj_.getPhysicsWorld()
      rigid_body = self.character_obj_.getRigidBody()
      if rigid_body.node().getNumShapes() <= 0:
        logging.warn("Rigid body contains no shapes, sweep collision test canceled")
        return
      
      aabb_shape = rigid_body.node().getShape(0)
      pos = self.character_obj_.getPos()
      height = self.character_obj_.getHeight()
      t0 = TransformState.makePos(Vec3(pos.getX(),0,pos.getZ() + 0.5* height))
      t1 = TransformState.makePos(Vec3(pos.getX(),0,pos.getZ() - 0.5* height))
      
      result = physics_world.sweepTestClosest(aabb_shape,t0,t1,CollisionMasks.LEVEL_OBSTACLE,0.0)
      
      logging.debug("Bottom at z pos %f"%(self.character_obj_.getBottom()))
      if not result.hasHit():
        logging.debug("No collision from collision sweep closest test from %s to %s "%(t0.getPos(),t1.getPos()))
      else:
        logging.debug("Found collision at point %s between p0: %s to p1 %s"%(result.getHitPos(),t0.getPos(),t1.getPos()))
        
      pos_at_hit = result.getHitPos()
      self.character_obj_.clampBottom(pos_at_hit.getZ())   
  
    def turnNone(self,action):
      self.character_obj_.getStatus().momentum.setX(0)
      
    def turnRight(self,action):   
      if not self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(True)
      self.character_obj_.getStatus().momentum.setX(self.character_obj_.character_info_.run_speed)
      
    def turnLeft(self,action):
      if self.character_obj_.isFacingRight():
        self.character_obj_.faceRight(False)
      self.character_obj_.getStatus().momentum.setX(self.character_obj_.character_info_.run_speed)     

      
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
      self.character_obj_.animate(self.animation_key_)  
      self.character_obj_.getStatus().air_jumps_count = 0
      self.character_obj_.getStatus().air_dashes_count = 0
      
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
      
      
      
        
      
      
      
    
      
      
    
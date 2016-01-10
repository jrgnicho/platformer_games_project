import logging
from panda3d.core import NodePath
from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletGenericConstraint
from panda3d.bullet import BulletWorld
from docutils import TransformSpec
from panda3d.core import Vec3
from panda3d.core import LPoint3
from panda3d.core import BoundingVolume
from panda3d.core import BoundingBox

from physics_platformer.collision import CollisionMasks
from physics_platformer.sprite import SpriteAnimator
from physics_platformer.animation import AnimationActor
from physics_platformer.character import CharacterInfo
from physics_platformer.game_object import AnimationSpriteAlignment
from physics_platformer.game_object import AnimatableObject
from physics_platformer.character.character_status import *
from physics_platformer.character.character_states import *
from physics_platformer.character import MotionCommander
from physics_platformer.state_machine import Action
from physics_platformer.state_machine import State
from physics_platformer.state_machine import StateMachine
from physics_platformer.state_machine import StateEvent
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.game_actions import *
from physics_platformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import CharacterStates


class CharacterBase(AnimatableObject):
  
  ANIMATOR_MASS_RATIO = 0.1 # The animator mass will be 10% the mass of the rigid body
  
  def  __init__(self,info):
    
    # animation base setup
    self.character_info_ = info   
    size = Vec3(info.width, AnimationActor.DEFAULT_WIDTH , info.height)
    AnimatableObject.__init__(self,info.name,size,info.mass)    
    self.animation_root_np_.setPos(Vec3(0,0,0))
    
        # constraints
    self.left_constraint_ = None
    self.right_constraint_ = None
    self.selected_constraint_ = None
    
    # rigid body
    shapes = self.node().getShapes()
    for shape in shapes:
      self.node().removeShape(shape)
      
    box_shape = BulletBoxShape(self.size_/2) 
    self.node().addShape(box_shape,TransformState.makePos(Vec3(0,0,0.5*size.getZ()))) # box bottom center coincident with the origin
    self.node().setMass(self.character_info_.mass)
    self.node().setLinearFactor((1,0,1))   
    self.node().setAngularFactor((0,0,0)) 
    self.setCollideMask(CollisionMasks.NO_COLLISION)    
    
    #  setting bounding volume
    min = LPoint3(-0.5*size.getX(),-0.5*size.getY(),0)
    max = LPoint3(0.5*size.getX(),0.5*size.getY(),size.getZ())
    self.node().setBoundsType(BoundingVolume.BT_box)    
    self.node().setBounds(BoundingBox(min,max))
    
    # character status
    self.status_ = CharacterStatus()
    
    # state machine
    self.sm_ = StateMachine()     
    
    # motion commander
    self.motion_commander_ = MotionCommander(self)
    
  def setup(self):    

    self.__setupDefaultStates__()
    self.__setupTransitionRules__()
    
    return True
  
  def setRigidBodyActive(self,active,force):
    self.node().setActive(active,force)
    if self.getAnimatorActor().getRigidBody() is not None:
      self.getAnimatorActor().getRigidBody().node().setActive(active,force)
  
  def enableFriction(self,enable,friction = None):
    
    if self.getAnimatorActor().getRigidBody() is None:
      return
    
    friction = self.character_info_.friction if friction is  None else friction
    if enable:
      self.getAnimatorActor().getRigidBody().node().setFriction(friction)
    else:
      self.getAnimatorActor().getRigidBody().node().setFriction(0)
      
    self.status_.friction_enabled = enable
  
  def getStatus(self):
    '''
    Returns a CharacterStatus instance
    '''
    return self.status_
  
  def getInfo(self):
    '''
    Returns a CharacterInfo instance
    '''
    return self.character_info_
  
  def getTop(self):
    return self.getAnimatorActor().getRigidBodyBoundingBox().top + self.getZ()
    
  def getBottom(self):
    return  self.getAnimatorActor().getRigidBodyBoundingBox().bottom + self.getZ()
  
  def getLeft(self):
    return self.getBack() if self.isFacingRight() else self.getFront()
  
  def getRight(self):
    return self.getFront() if self.isFacingRight() else self.getBack()
    
  def getFront(self):
    return (1.0 if self.isFacingRight() else -1.0)*self.getAnimatorActor().getRigidBodyBoundingBox().right + self.getX()
    
  def getBack(self):
    return (1.0 if self.isFacingRight() else -1.0)*self.getAnimatorActor().getRigidBodyBoundingBox().left + self.getX()
  
  def clampLeft(self,x):
    
    vel = self.node().getLinearVelocity()
    vel.setX(0)
    self.node().setLinearVelocity(vel)
    
    local_offset = self.getBack() if self.isFacingRight() else self.getFront()
    local_offset = self.getX() - local_offset
    
    self.__deactivateConstraint__() # avoids recoil due to rapid position change
    self.setX(x + local_offset)
    self.__activateConstraint__(self.selected_constraint_)
    
  def clampOriginX(self,x):
    vel = self.node().getLinearVelocity()
    vel.setX(0)
    self.node().setLinearVelocity(vel)  
    
    self.__deactivateConstraint__() # avoids recoil due to rapid position change     
    self.setX(x)
    self.__activateConstraint__(self.selected_constraint_)
    
  def clampRight(self,x):
    
    vel = self.node().getLinearVelocity()
    vel.setX(0)
    self.node().setLinearVelocity(vel)
    
    local_offset = self.getFront() if self.isFacingRight() else self.getBack()
    local_offset = self.getX() - local_offset
    
    self.__deactivateConstraint__() # avoids recoil due to rapid position change
    self.setX(x + local_offset) 
    self.__activateConstraint__(self.selected_constraint_)   
  
  def clampBottom(self,z):
    '''
    Character.clampDown(double )
      Sets the bottom z value of the character
    '''
    
    # setting vertical speed to zero
    vel = self.node().getLinearVelocity()
    vel.setZ(0)
    self.node().setLinearVelocity(vel)
    
    # placing bottom at z value
    bbox = self.getAnimatorActor().getRigidBodyBoundingBox()  
    self.__deactivateConstraint__() # avoids recoil due to rapid position change
    self.setZ(z - bbox.bottom) 
    self.__activateConstraint__(self.selected_constraint_)
  
  def clampTop(self,z):
    '''
    Character.clampDown(double )
      Sets the Top z value of the character
    '''
    
    # setting vertical speed to zero
    vel = self.node().getLinearVelocity()
    vel.setZ(0)
    self.node().setLinearVelocity(vel)
    
    # placing top at z value
    bbox = self.getAnimatorActor().getRigidBodyBoundingBox()     
    self.__deactivateConstraint__() # avoids recoil due to rapid position change    
    self.setZ(z - bbox.top) 
    self.__activateConstraint__(self.selected_constraint_)
    
  def execute(self,action):
    self.sm_.execute(action)
    
  def update(self,dt):
    #self.node().setActive(True)
    self.sm_.execute(GeneralActions.GameStep(dt))
    
  # =========== Rigid Body Methods =========== #
  def setLinearVelocity(self,vel,apply_all = False):
    if apply_all and self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().node().setLinearVelocity(Vec3(0,0,0))        
    self.node().setLinearVelocity(vel) 
    
  def getLinearVelocity(self):
    return self.node().getLinearVelocity() 
    
  def clearForces(self):
    self.node().clearForces()    
    attached_rb = self.animator_.getRigidBody()
    if attached_rb is not None:
      attached_rb.node().clearForces()
      
  def applyCentralImpulse(self,impls):
    self.node().applyCentralImpulse(impls)
    
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
    
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.LAND.key, CharacterStateKeys.LANDING)
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.LAND_EDGE.key, CharacterStateKeys.EDGE_LANDING)
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.JUMP.key, CharacterStateKeys.AIR_JUMPING, lambda: self.getStatus().air_jump_count < self.getInfo().air_jumps)
    self.sm_.addTransition(CharacterStateKeys.FALLING,CharacterActions.DASH.key,CharacterStateKeys.MIDAIR_DASHING,lambda: self.getStatus().air_dashes_count < self.getInfo().air_dashes)
    
    self.sm_.addTransition(CharacterStateKeys.EDGE_LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.EDGE_LANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.EDGE_LANDING,CharacterActions.DASH.key,CharacterStateKeys.DASHING)
    
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CollisionAction.FREE_FALL,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.EDGE_RECOVERY.key,CharacterStateKeys.STANDING_EDGE_RECOVERY) 
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.DASH.key,CharacterStateKeys.DASHING)   
    
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,StateMachineActions.DONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.DASH.key,CharacterStateKeys.DASHING)
    
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.MOVE_NONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CollisionAction.FREE_FALL,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.DASH.key,CharacterStateKeys.DASHING)
    
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, StateMachineActions.DONE.key, CharacterStateKeys.JUMPING)
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.JUMPING, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.JUMPING,CharacterActions.DASH.key,CharacterStateKeys.MIDAIR_DASHING,lambda: self.getStatus().air_dashes_count < self.getInfo().air_dashes)
    
    self.sm_.addTransition(CharacterStateKeys.LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.LANDING, CollisionAction.FREE_FALL, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.LANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.LANDING,CharacterActions.DASH.key,CharacterStateKeys.DASHING) 
    
    self.sm_.addTransition(CharacterStateKeys.AIR_JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.AIR_JUMPING, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.AIR_JUMPING, CharacterActions.DASH.key,CharacterStateKeys.MIDAIR_DASHING,lambda: self.getStatus().air_dashes_count < self.getInfo().air_dashes)
    
    self.sm_.addTransition(CharacterStateKeys.DASHING,StateMachineActions.DONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.DASHING,CharacterActions.DASH_CANCEL.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.DASHING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.DASHING,CharacterActions.FALL.key,CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,StateMachineActions.DONE.key,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,CharacterActions.JUMP.key,CharacterStateKeys.AIR_JUMPING,lambda: self.getStatus().air_jump_count < self.getInfo().air_jumps)
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,CharacterActions.DASH_CANCEL.key,CharacterStateKeys.FALLING)
    
  def addAnimationActor(self,name,anim_actor,
                        align = (AnimationSpriteAlignment.CENTER_OFFSET_ALIGN),
                        center_offset = Vec3(0,0,0)):
    if type(anim_actor) != AnimationActor:
      logging.error("Second argument is not of type 'AnimationActor'")
      return False
    
    self.addSpriteAnimation(name, anim_actor, align, center_offset)
    
    if (self.animator_np_ is None):
      self.pose(name)
      
      
  def getAnimatorActor(self):
    if self.animator_ is None:
      return None    
    return self.animator_    
    
  def pose(self,animation_name, frame = 0):
    
    if (self.physics_world_ is None) or (self.getParent().isEmpty()):
      logging.warning("PhysicsWorld or Parent NodePath have not been set on the Character object, pose can not be selected")
      return False
    
    if not self.animators_.has_key(animation_name):
      logging.warning( "Invalid animation name '%s'"%(animation_name))
      return False
    
    if self.selected_animation_name_ == animation_name:
        logging.warning(" Animation %s already selected"%(animation_name))
        return True      
    
    # cleaning up constraints
    self.__cleanupConstraints__()
        
    # deactivating current animator
    face_right = True
    if self.animator_np_ != None :
        
        face_right = self.animator_.isFacingRight()
        self.animator_.deactivate()   
    self.animator_np_ = self.animators_[animation_name]   
    self.animator_ = self.animator_np_.node().getPythonTag(SpriteAnimator.__name__)  
    self.animator_.activate(self.physics_world_,self.getParent())  
    self.__setupConstraints__(self.animator_.getRigidBody())    
    
    self.selected_animation_name_ = animation_name     
    self.faceRight(face_right)
    self.animator_.pose(frame) 
    self.enableFriction(self.getStatus().friction_enabled)
      
    return True 
    
  def faceRight(self,face_right = True):
    constraint = self.right_constraint_ if face_right else self.left_constraint_
    self.__activateConstraint__(constraint)
    
    if self.animator_np_ is not None :
      self.animator_.faceRight(face_right)
        
  def __setupConstraints__(self,actor_rigid_body_np):
    
    self.__cleanupConstraints__()
    
    self.left_constraint_ = BulletGenericConstraint(self.node(),
                                                    actor_rigid_body_np.node(),
                                                    TransformState.makeIdentity(),
                                                    TransformState.makeHpr(Vec3(180,0,0)),False)
    
    self.right_constraint_ = BulletGenericConstraint(self.node(),
                                                     actor_rigid_body_np.node(),
                                                     TransformState.makeIdentity(),
                                                     TransformState.makeIdentity(),False)
    
    self.left_constraint_.setEnabled(False)
    self.right_constraint_.setEnabled(False)
    for axis in range(0,6):
      self.left_constraint_.setParam(BulletGenericConstraint.CP_cfm,0,axis)
      self.right_constraint_.setParam(BulletGenericConstraint.CP_cfm,0,axis)
    
  def __cleanupConstraints__(self):
    
    if self.selected_constraint_ is not None:
      self.selected_constraint_.setEnabled(False)
      self.physics_world_.remove(self.selected_constraint_)
      
    self.left_constraint_ = None
    self.right_constraint_ = None
    self.selected_constraint_ = None
    
  def __deactivateConstraint__(self):
    
    if self.selected_constraint_ is not None:
      self.selected_constraint_.setEnabled(False)
      self.physics_world_.remove(self.selected_constraint_)
      
    
  def __activateConstraint__(self,constraint):
    
      if self.selected_constraint_ != constraint:
        
        # disabling active constraint
        self.__deactivateConstraint__()
        
      if not constraint.isEnabled():
        
        # placing actor rigid body relative to character's rigid body
        actorrb_np = self.animator_.getRigidBody()
        static = actorrb_np.node().isStatic()
        actorrb_np.node().setStatic(True)
        actorrb_np.setTransform(self,TransformState.makeIdentity())        
        if constraint == self.right_constraint_:
          actorrb_np.setH(self,0)
        else:
          actorrb_np.setH(self,180)
        actorrb_np.node().setStatic(static)
          
        self.selected_constraint_ = constraint
        self.selected_constraint_.setEnabled(True)
        self.physics_world_.attach(self.selected_constraint_)
          
        
    
          
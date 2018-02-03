from docutils import TransformSpec
import logging
from panda3d.bullet import BulletBoxShape, BulletGhostNode, BulletSphereShape
from panda3d.bullet import BulletGenericConstraint
from panda3d.bullet import BulletWorld
from panda3d.core import BoundingBox
from panda3d.core import BoundingVolume
from panda3d.core import LPoint3
from panda3d.core import NodePath
from panda3d.core import TransformState
from panda3d.core import Vec3

from physics_platformer.animation import AnimationActor
from physics_platformer.character import CharacterInfo
from physics_platformer.character import MotionCommander
from physics_platformer.character.character_states import *
from physics_platformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import CharacterStates
from physics_platformer.character.character_status import *
from physics_platformer.collision import CollisionMasks
from physics_platformer.game_actions import *
from physics_platformer.game_object import GameObject, AnimatableObject
from physics_platformer.game_object import AnimationSpriteAlignment
from physics_platformer.sprite import SpriteAnimator
from physics_platformer.state_machine import Action
from physics_platformer.state_machine import State
from physics_platformer.state_machine import StateEvent
from physics_platformer.state_machine import StateMachine
from physics_platformer.state_machine import StateMachineActions


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
    box_shape.setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
    self.node().addShape(box_shape,TransformState.makePos(Vec3(0,0,0.5*size.getZ()))) # box bottom center coincident with the origin
    self.node().setMass(self.character_info_.mass)
    self.node().setLinearFactor((1,1,1)) 
    self.node().setAngularFactor((0,0,0)) 
    self.setCollideMask(CollisionMasks.NO_COLLISION)    
    
    #  setting bounding volume
    min = LPoint3(-0.5*size.getX(),-0.5*size.getY(),0)
    max = LPoint3(0.5*size.getX(),0.5*size.getY(),size.getZ())
    self.node().setBoundsType(BoundingVolume.BT_box)    
    self.node().setBounds(BoundingBox(min,max))
    
    # setting origin ghost nodes
    rel_pos = Vec3(-GameObject.ORIGIN_XOFFSET,0,info.height/2)
    self.left_origin_gn_ = self.attachNewNode(BulletGhostNode(self.getName() + '-left-origin'))
    self.left_origin_gn_.node().addShape(BulletSphereShape(GameObject.ORIGIN_SPHERE_RADIUS),TransformState.makePosHpr(rel_pos,Vec3.zero()))
    self.left_origin_gn_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_ORIGIN if not self.isFacingRight() else CollisionMasks.NO_COLLISION)
    
    rel_pos = Vec3(GameObject.ORIGIN_XOFFSET,0,info.height/2)
    self.right_origin_gn_ = self.attachNewNode(BulletGhostNode(self.getName() + '-right-origin'))
    self.right_origin_gn_.node().addShape(BulletSphereShape(GameObject.ORIGIN_SPHERE_RADIUS),TransformState.makePosHpr(rel_pos,Vec3.zero()))
    self.right_origin_gn_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_ORIGIN if self.isFacingRight() else CollisionMasks.NO_COLLISION)
    
    # character status
    self.status_ = CharacterStatus()
    
    # state machine
    self.sm_ = StateMachine()     
    
    # motion commander
    self.motion_commander_ = MotionCommander(self)
    
    # set id
    self.setObjectID(self.getName())
    
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
    
  def setPhysicsWorld(self,physics_world):
    GameObject.setPhysicsWorld(self,physics_world)
    self.physics_world_.attach(self.left_origin_gn_.node())
    self.physics_world_.attach(self.right_origin_gn_.node())
    
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
  
  def getHeight(self):
    return self.getTop() - self.getBottom()
  
  def getWidth(self):
    return self.getRight() - self.getLeft()
  
  def getTop(self):
    '''
    getTop()
      Returns the z value of the top side relative the the movement reference node
    '''
    ref_np = self.reference_np_
    return self.getAnimatorActor().getRigidBodyBoundingBox().top + self.getZ(ref_np)
    
  def getBottom(self):
    '''
    getBottom()
      Returns the z value of the bottom side relative the the movement reference node
    '''
    ref_np = self.reference_np_
    return  self.getAnimatorActor().getRigidBodyBoundingBox().bottom + self.getZ(ref_np)
  
  def getLeft(self):
    '''
    getLeft()
      Returns the x value of the left side relative the the movement reference node
    '''
    return self.getBack() if self.isFacingRight() else self.getFront()
  
  def getRight(self):
    '''
    getRight()
      Returns the x value of the right side relative the the movement reference node
    '''
    return self.getFront() if self.isFacingRight() else self.getBack()
    
  def getFront(self):
    '''
    getFront()
      Returns the x value of the front side relative the the movement reference node
    '''
    ref_np = self.reference_np_
    dx = (1.0 if self.isFacingRight() else -1.0)*self.getAnimatorActor().getRigidBodyBoundingBox().right
    rel_pos = ref_np.getRelativePoint(self,Vec3(dx,0,0))
    return rel_pos.getX()
    
  def getBack(self):
    '''
    getBack()
      Returns the x value of the back side relative the the movement reference node
    '''
    ref_np = self.reference_np_
    dx = (1.0 if self.isFacingRight() else -1.0)*self.getAnimatorActor().getRigidBodyBoundingBox().left
    rel_pos = ref_np.getRelativePoint(self,Vec3(dx,0,0))
    return rel_pos.getX()
  
  def clampLeft(self,x):
    
    vel = self.getLinearVelocity()
    vel.setX(0)
    self.setLinearVelocity(vel)
    
    ref = self.reference_np_
    local_offset = self.getBack() if self.isFacingRight() else self.getFront()
    local_offset = self.getX(ref) - local_offset
    
    self.setX(ref,x + local_offset)
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setX(ref,x + local_offset)
    
  def clampOriginX(self,x):
    vel = self.getLinearVelocity()
    vel.setX(0)
    self.setLinearVelocity(vel)  
    
    ref = self.reference_np_   
    self.setX(ref,x)
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setX(ref,x)
    
  def clampRight(self,x):
    
    vel = self.getLinearVelocity()
    vel.setX(0)
    self.setLinearVelocity(vel)
    
    ref = self.reference_np_
    local_offset = self.getFront() if self.isFacingRight() else self.getBack()
    local_offset = self.getX(ref) - local_offset    
    
    self.setX(ref,x + local_offset) 
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setX(ref,x + local_offset)
    
  def clampFront(self,x):
    if self.isFacingRight():
      self.clampRight(x)
    else:
      self.clampLeft(x)
      
  def clampBack(self,x):
    if self.isFacingRight():
      self.clampLeft(x)
    else:
      self.clampRight(x)
  
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
    ref = self.reference_np_
    bbox = self.getAnimatorActor().getRigidBodyBoundingBox()  
    self.setZ(ref,z - bbox.bottom) 
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setZ(ref,z - bbox.bottom)
      
  def clampBottomToSurface(self):
    """
      Places the bottom of the character's bounding box on the nearest surface that's below the character
    """
    
    result = self.doCollisionSweepTestZ()
    parent = self.getParent()
    ref_node = self.getReferenceNodePath()
     
    if result.hasHit():
      
      self.node().setLinearFactor(LVector3(1,1,0))   # disable movement in z
      ref_pos = ref_node.getRelativePoint(parent,result.getHitPos())
      self.clampBottom(ref_pos.getZ())               # place bottom at hit point
      self.node().setLinearFactor(LVector3(1,1,1))   # enable movement in z 
      
    return result.hasHit()
  
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
    ref = self.reference_np_
    bbox = self.getAnimatorActor().getRigidBodyBoundingBox()       
    self.setZ(ref,z - bbox.top) 
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setZ(ref,z - bbox.top)
    
  def setPos(self, *args ):
    '''
    setPos(NodeHandle ref_nh, Vec3 pos)
    setPos(Vec3 pos)
    '''
    
    ref_np , pos = self.__parseTransformArgs__(args)
    if len(args) == 2:
      ref_np = args[0]
      pos = args[1]
    if len(args) == 1:
      pos = args[0]    
      
    # setting position   
    NodePath.setPos(self,ref_np,pos)    
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setPos(ref_np,pos)   
      
  def setX(self, *args):
    
    ref_np , pos = self.__parseTransformArgs__(args)
    if len(args) == 2:
      ref_np = args[0]
      val = args[1]
    if len(args) == 1:
      val = args[0] 
    
    NodePath.setX(self,ref_np,val)
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setX(ref_np,val)   
      
  def setY(self, *args):
    
    ref_np , pos = self.__parseTransformArgs__(args)
    if len(args) == 2:
      ref_np = args[0]
      val = args[1]
    if len(args) == 1:
      val = args[0] 
    
    NodePath.setY(self,ref_np,val)
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setY(ref_np,val) 
      
  def setZ(self, *args):
    
    ref_np , pos = self.__parseTransformArgs__(args)
    if len(args) == 2:
      ref_np = args[0]
      val = args[1]
    if len(args) == 1:
      val = args[0] 
    
    NodePath.setZ(self,ref_np,val)
    if self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().setZ(ref_np,val) 
    
    
  def setStatic(self,static):
    '''
    setStatic(Bool static)
    Sets the static property to either True or False.
    '''
         
    self.node().setStatic(static)
    self.getAnimatorActor().getRigidBody().node().setStatic(static)
    pos = self.getAnimatorActor().getRigidBody().getPos()
    NodePath.setPos(self,pos)
    
    if static:
      self.__deactivateConstraint__()
    else:
      self.__activateConstraint__(self.selected_constraint_)    
    
    
  def execute(self,action):
    self.sm_.execute(action)
    
  def update(self,dt):
    self.sm_.execute(GeneralActions.GameStep(dt))
    
  # =========== Rigid Body Methods =========== #
  def setLinearVelocity(self,vel,clear_all = False):
    '''
    setLinearVelocity(Vec3 vel,Bool clear_all = False)
      Applies a velocity vector to the Character.  The vector is assumed to 
      be relative the the Character's reference node
    '''
    
    # converting to world coordinates
    vel = self.getParent().getRelativeVector(self.reference_np_,vel)
    
    if clear_all and self.getAnimatorActor() is not None:
      self.getAnimatorActor().getRigidBody().node().setLinearVelocity(Vec3(0,0,0))        
    self.node().setLinearVelocity(vel) 
    
  def getLinearVelocity(self):
    '''
    getLinearVelocity() -> Vec3
      Returns the velocity vecor expressed in the Character's Reference NodePath
    '''
    return self.reference_np_.getRelativeVector(self.getParent(), self.node().getLinearVelocity())
    
  def clearForces(self):
    self.node().clearForces()    
    attached_rb = self.animator_.getRigidBody()
    if attached_rb is not None:
      attached_rb.node().clearForces()
      
  def applyCentralImpulse(self,impls):
    impls = self.getParent().getRelativeVector(self.reference_np_,impls)
    self.node().applyCentralImpulse(impls)
    
  # ============== Private Methods ====================== #
  def __parseTransformArgs__(self,*args):
    ref_np = self.reference_np_
    val = None
    if len(args) == 2:
      ref_np = args[0]
      val = args[1]
    if len(args) == 1:
      val = args[0] 
    
    return (ref_np,val)
    
    
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
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.JUMP.key, CharacterStateKeys.AIR_JUMPING, lambda: self.getStatus().air_jumps_count < self.getInfo().air_jumps)
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
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,CharacterActions.JUMP.key,CharacterStateKeys.AIR_JUMPING,lambda: self.getStatus().air_jumps_count < self.getInfo().air_jumps)
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,CharacterActions.DASH_CANCEL.key,CharacterStateKeys.FALLING)
    
  def addAnimationActor(self,name,anim_actor,
                        align = (AnimationSpriteAlignment.CENTER_OFFSET_ALIGN),
                        center_offset = Vec3(0,0,0)):
    if type(anim_actor) != AnimationActor:
      logging.error("Second argument is not of type 'AnimationActor'")
      return False
    
    self.addSpriteAnimation(name, anim_actor, align, center_offset)
    anim_actor.setPythonTag(GameObject.ID_PYTHON_TAG,self.getName())
    
    if (self.animator_np_ is None):
      self.pose(name)  
      
  def getActionGhostBody(self):   
    '''
    Returns the Node Path to the BulletGhost node containing the action body
    '''
    return self.animator_.getActionGhostBody() if (self.animator_ is not None) else None
  
  def getHitBox(self):
    '''
    Returns the Node Path to the BulletGhost node containing the hit bounding box
    '''
    return self.animator_.getHitBox() if (self.animator_ is not None) else None
  
  def getDamageBox(self):
    '''
    Returns the Node Path to the BulletGhost node containing the damage bounding box
    '''
    return self.animator_.getDamageBox() if (self.animator_ is not None) else None
  
  def getRigidBody(self):
    '''
    Returns the Node Path to the BulletRigidBody node containing the character's AABB
    '''
    return self.animator_.getRigidBody() if (self.animator_ is not None) else None
      
  def getAnimatorActor(self):
    if self.animator_ is None:
      return None    
    return self.animator_    
    
  def pose(self,animation_name, frame = 0):
    
    if (self.physics_world_ is None) or (self.getParent().isEmpty()):
      logging.warning("PhysicsWorld or Parent NodePath have not been set on the Character object, pose can not be selected")
      return False
    
    if animation_name not in self.animators_:
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
  
  def doCollisionSweepTestZ(self,col_mask = CollisionMasks.LEVEL_OBSTACLE,from_z = 0, to_z = 0):
    '''
    doCollisionSweepTestZ(double from_z = 0, double to_z = 0)
    Performs a collision sweep test along z in order to determine the height 
    at which the character's active rigid body comes into contact with an obstacle.  This is useful during 
    landing actions.
    
    @param col_mask: [optional] collision mask of the object(s) to check for collisions with.
    @param from_z:   [optional] z value for the start position
    @param to_z:     [optional] z value for the end position  
    '''
    
    pos = self.getPos()
    if abs(from_z - to_z) < 1e-5:
      height = self.getHeight()
      from_z = pos.getZ() + 0.5* height
      to_z = pos.getZ() - 0.5* height
    t0 = TransformState.makePos(Vec3(pos.getX(),pos.getY(),from_z))
    t1 = TransformState.makePos(Vec3(pos.getX(),pos.getY(),to_z))
    
    rigid_body = self.getRigidBody()
    if rigid_body.node().getNumShapes() <= 0:
      logging.warn("Rigid body contains no shapes, collision sweep test canceled")
      return
    
    aabb_shape = rigid_body.node().getShape(0)
    result = self.physics_world_.sweepTestClosest(aabb_shape,t0,t1,col_mask,0.0)

    if not result.hasHit():
      logging.warn("No collision from collision sweep closest test from %s to %s "%(t0.getPos(),t1.getPos()))
    else:
      logging.debug("Found collision at point %s between p0: %s to p1 %s"%(result.getHitPos(),t0.getPos(),t1.getPos()))
      
    return result
    
  def faceRight(self,face_right = True):
    constraint = self.right_constraint_ if face_right else self.left_constraint_
    self.__activateConstraint__(constraint)
    
    if self.animator_np_ is not None :
      self.animator_.faceRight(face_right)
      
    if face_right:
      self.right_origin_gn_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_ORIGIN)
      self.left_origin_gn_.node().setIntoCollideMask(CollisionMasks.NO_COLLISION)
    else:
      self.left_origin_gn_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_ORIGIN)
      self.right_origin_gn_.node().setIntoCollideMask(CollisionMasks.NO_COLLISION)
      
        
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
        self.node().setStatic(static)
          
        self.selected_constraint_ = constraint
        self.selected_constraint_.setEnabled(True)
        self.physics_world_.attach(self.selected_constraint_)
          
        
    
          
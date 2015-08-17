
from panda3d.core import Vec3
from physics_platformer.animation import AnimationActor
from physics_platformer.game_object import CharacterInfo
from physics_platformer.game_object import AnimationSpriteAlignment
from physics_platformer.game_object import AnimatableObject
from panda3d.core import TransformState
from panda3d.bullet import BulletGenericConstraint
from docutils import TransformSpec


class CharacterObject(AnimatableObject):
  
  def  __init__(self,info):
    
    self.character_info_ = info
    
    # turning active rigid bodies left and right
    self.left_constraint_ = None
    self.right_constraint_ = None
    self.active_constraint_ = None
    
    size = Vec3(info.width, AnimationActor.DEFAULT_WIDTH , info.height)
    AnimatableObject.__init__(self,info.name,size,info.mass,None)
    
    # re-creating shape
    shapes = self.rigid_body_np_.node().getNumShapes()
    for shape in shapes:
      self.rigid_body_np_.node().removeShape(shape)
      
    box_shape = BulletBoxShape(self.size_/2) 
    self.rigid_body_np_.node().addShape(box_shape,TransformState.makePos(Vec3(0,0,0.5*size.getZ()))) # box bottom center coincident with the origin
    self.rigid_body_np_.node().setMass(mass)
    self.rigid_body_np_.node().setLinearFactor((1,0,1))   
    self.rigid_body_np_.node().setAngularFactor((0,0,0)) 
    self.rigid_body_np_.setCollideMask(CollisionMasks.NONE)
  
  def setParentPhysicsWorld(self,physics_world): 
    if type(physics_world) is not BulletWorld:
      logging.error( "Object is not of type %s"%(str(type(BulletWorld))) )      
    self.physics_world_ = physics_world
      
  def setParentNodePath(self,np):
    if type(np) is not NodePath:
      logging.error("Passed parent node path is not of type "%( str(type(NodePath) )))      
    self.parent_np_ = np

    
  def addAnimationActor(self,name,anim_actor,
                        align = (AnimationSpriteAlignment.BOTTOM_CENTER_ALIGN),
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
    
    if (self.physics_world_ is None) or (self.parent_np_ is None):
      logging.error("PhysicsWorld or Parent NodePath have not been set on the Character object, pose can not be selected")
      return False
    
    if not self.animators_.has_key(animation_name):
      logging.error( "Invalid animation name '%s'"%(animation_name))
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
    self.animator_.activate(self.physics_world_,self.parent_np_)  
    self.__setupConstraints__(self.animator_.getRigidBody()) 
    
    
    self.selected_animation_name_ = animation_name     
    self.faceRight(face_right)
    self.animator_.pose(frame) 
      
    return True 
    
  def faceRight(self,face_right = True):
    constraint = self.right_constraint_ if face_right else self.left_constraint_
    self.__activateConstraint__(constraint)
    
    if self.animator_np_ != None :
        self.animator_.faceRight(face_right)
        
  def __setupConstraints__(self,actor_rigid_body_np):
    
    self.__cleanupConstraints__()
    
    self.left_constraint_ = BulletGenericConstraint(self.rigid_body_np_.node(),
                                                    actor_rigid_body_np.node(),
                                                    TransformState.makeIdentity(),
                                                    TransformState.makeHpr(Vec3(180,0,0)),False)
    
    self.right_constraint_ = BulletGenericConstraint(self.rigid_body_np_.node(),
                                                     actor_rigid_body_np.node(),
                                                     TransformState.makeIdentity(),
                                                     TransformState.makeIdentity(),False)
    
    self.left_constraint_.setEnabled(False)
    self.right_constraint_.setEnabled(False)
    
  def __cleanupConstraints__(self):
    
    if self.active_constraint_ is not None:
      self.active_constraint_.setEnabled(False)
      self.physics_world_.remove(self.active_constraint_)
      
    self.left_constraint_ = None
    self.right_constraint_ = None
    self.active_constraint_ = None
    
  def __activateConstraint__(self,constraint):
    
      if self.active_constraint_ != constraint:
        
        # disabling active constraint
        if self.active_constraint_ is not None:
          self.active_constraint_.setEnabled(False)
          self.physics_world_.remove(self.active_constraint_)
        
        # placing actor rigid body relative to character's rigid body
        actorrb_np = self.animator_.getRigidBody()
        static = actorrb_np.node().isStatic()
        actorrb_np.node().setStatic(True)
        actorrb_np.setTransform(self.rigid_body_np_,TransformState.makeIdentity())        
        if constraint == self.right_constraint_:
          actorrb_np.setH(self.rigid_body_np_,0)
        else:
          actorrb_np.setH(self.rigid_body_np_,180)
        actorrb_np.node().setStatic(static)
          
        self.active_constraint_ = constraint
        self.active_constraint_.setEnabled(True)
        self.physics_world_.attach(self.active_constraint_)
          
        
    
          
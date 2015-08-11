from physics_platformer.animation import AnimationActor
from physics_platformer.game_object import AnimatableObject


class CharacterObject(AnimatableObject):
  
  def  __init__(self,name):
    
    AnimatableObject.__init__(self,name,(40,60),1,None)
    self.physics_world_ = None   
  
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
    
    if (self.animator_np_ == None) and (self.physics_world_ is not None):
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
    
    # detaching from rigid body
    self.detachNode()        
    
    #deactivating current animator
    face_right = True
    if self.animator_np_ != None :
        
        face_right = self.animator_.isFacingRight()
        self.animator_.deactivate()
            
    self.animator_np_ = self.animators_[animation_name]   
    self.animator_ = self.animator_np_.node().getPythonTag(SpriteAnimator.__name__)  
    self.animator_.activate(self.physics_world_,self.parent_np_)   
    self.animator_.faceRight(face_right)
    self.animator_.pose(frame)
    self.selected_animation_name_ = animation_name    

    # reparenting to animator rigid body
    self.rigid_body_np_ = self.animator_.getRigidBody()
    self.reparentTo(self.rigid_body_np_)     
      
    return True 
    
  def faceRight(self,face_right = True):
    if self.animator_np_ != None :
        self.animator_.faceRight(face_right)
          
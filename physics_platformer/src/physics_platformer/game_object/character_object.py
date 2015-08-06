from physics_platformer.animation import AnimationActor
from physics_platformer.game_object import AnimatableObject
from twisted.trial.runner import LoggedSuite

class CharacterObject(AnimatableObject):
  
  def  __init__(self,name):
    
    AnimatableObject.__init__(self,name,(40,60),1,None)
    self.physics_world_ = None
   
   
  def setParentPhysicsWorld(self,physics_world): 
    self.physics_world_ = physics_world
    
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
    
    if self.selected_animation_name_ == animation_name:
        logging.warning(" Animation %s already selected"%(animation_name))
        return True      
    
    self.detachNode()     
    
    # removing rigid body from scene
    parent_np = None
    if self.rigid_body_np_ is not None: 
      parent_np = self.rigid_body_np_.getParent() if self.rigid_body_np_.hasParent() else None
      self.rigid_body_np_.detachNode()
      self.physics_world_.removeRigidBody(self.rigid_body_np_.node())
      
      
    if not AnimatableObject.pose(self,animation_name,frame):
      return False    
    
    # reparenting to animator rigid body
    self.rigid_body_np_ = self.animator_.getRigidBody()
    self.rigid_body_np_.reparentTo(parent_np)
    self.reparentTo(self.rigid_body_np_)   
    self.physics_world_.attachRigidBody(self.rigid_body_np_.node())     
      
    return True 
    
  def faceRight(self,face_right = True):
    if self.animator_np_ != None :
        self.animator_.faceRight(face_right)
          
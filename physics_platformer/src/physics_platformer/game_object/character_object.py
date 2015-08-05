from physics_platformer.animation import AnimationActor
from physics_platformer.game_object import AnimatableObject
from twisted.trial.runner import LoggedSuite

class CharacterObject(AnimatableObject):
  
  def  __init__(self,name):
    
    AnimatableObject.__init__(self,name,(40,60),1,None)
    self.clear()
    
    
  def addAnimationActor(self,name,anim_actor,
                        align = (AnimationSpriteAlignment.BOTTOM_CENTER_ALIGN),
                        center_offset = Vec3(0,0,0)):
    if type(anim_actor) != AnimationActor:
      logging.error("Second argument is not of type 'AnimationActor'")
      return False
    
    self.addSpriteAnimation(name, anim_actor, align, center_offset)
    
    if self.animator_np_ == None:
      self.pose(name)
      
  def getAnimatorActor(self):
    if self.animator_ is None:
      return None
    
    return self.animator_.getPythonTag(AnimationActor.__name__)
    
    
    def pose(self,animation_name, frame = 0):
        
        if not self.animators_.has_key(animation_name):
            logging.error( "Invalid animation name '%s'"%(animation_name))
            return False
        
        if self.selected_animation_name_ == animation_name:
            logging.warning(" Animation %s already selected"%(animation_name))
            return True
        
        # deselecting current node
        face_right = True
        if self.animator_np_ != None :
            
            face_right = self.animator_.isFacingRight()
            self.animator_.stop()
            self.animator_np_.hide()
            
        self.animator_np_ = self.animators_[animation_name]   
        self.animator_ = self.animator_np_.node().getPythonTag(AnimationActor.__name__)            
        self.animator_.pose(frame) 
        self.faceRight(face_right)
        self.animator_np_.show()   
        self.selected_animation_name_ = animation_name    
        
        return True 
      
    def faceRight(self,face_right = True):
      if self.animator_np_ != None :
          self.animator_.faceRight(face_right)
          angle = 0 if face_right else 180
          self.animation_root_np_.setR(-angle)
          
from physics_platformer.state_machine import Action

class AnimationAction(Action):
  
  def __init__(self,key,animation_name = '',current_frame = 0,num_frames = 0):
    
    Action.__init__(self,key)
    self.name = animation_name
    self.current_frame = current_frame
    self.num_frames = num_frames
    

class AnimationActions(object):
  
  ANIMATION_STARTED = AnimationAction('ANIMATION_STARTED')
  ANIMATION_COMPLETED = AnimationAction('ANIMATION_COMPLETED')
  ANIMATION_FRAME_STARTED = AnimationAction('ANIMATION_FRAME_STARTED')
  ANIMATION_FRAME_COMPLETED = AnimationAction('ANIMATION_FRAME_COMPLETED')
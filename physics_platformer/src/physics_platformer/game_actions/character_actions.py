from physics_platformer.game_actions import AnimationAction

class CharacterAction(AnimationAction):
  

  
  def __init__(self,key,animation_name = None):
    
    
    if animation_name is None:
      animation_name = key
      
    AnimationAction.__init__(self,key,animation_name)
    
    
class CharacterActions(object):
    
  MOVE_RIGHT = CharacterAction('MOVE_RIGHT')
  MOVE_LEFT = CharacterAction('MOVE_LEFT')
  MOVE_UP = CharacterAction("MOVE_UP")
  MOVE_DOWN = CharacterAction("MOVE_DOWN")
  MOVE_NONE = CharacterAction("MOVE_NONE")
  JUMP = CharacterAction('JUMP')
  JUMP_CANCEL = CharacterAction('JUMP_CANCEL')
  DASH = CharacterAction('DASH')
  HALT = CharacterAction('HALT')
  FALL = CharacterAction('FALL')
  EDGE_RECOVERY = CharacterAction('EDGE_RECOVERY')
  LAND_EDGE = CharacterAction('LAND_EDGE')
    
from physics_platformer.game_actions import AnimationAction

class CharacterAction(Action):
  
  MOVE_RIGHT = CharacterAction('MOVE_RIGHT')
  MOVE_LEFT = CharacterAction('MOVE_LEFT')
  MOVE_UP = CharacterAction("MOVE_UP")
  MOVE_DOWN = CharacterAction("MOVE_DOWN")
  JUMP = CharacterAction('JUMP')
  DASH = CharacterAction('DASH')
  HALT = CharacterAction('DASH_HALT')
  
  def __init__(self,key,animation_name = None):
    
    
    if animation_name is None:
      animation_name = key
      
    AnimationAction.__init__(self,key,animation_name)
    
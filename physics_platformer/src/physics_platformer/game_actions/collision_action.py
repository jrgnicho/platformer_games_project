from physics_platformer.state_machine import Action

class CollisionAction(Action):
  
  
  DELIVER_HIT = 'DELIVER_HIT'
  TAKE_HIT = 'TAKE_HIT'
  ACTION_BODY_OVERLAP = 'ACTION_BODY_OVERLAP'
  COLLIDE_LANDING_SURFACE = 'LAND'
  COLLIDE_CEILING = 'COLLIDE_CEILING'
  COLLIDE_LEFT_WALL = 'COLLIDE_LEFT_WALL'
  COLLIDE_RIGHT_WALL = 'COLLIDE_RIGHT_WALL'
  COLLIDE_LEVEL_BOUND = 'COLLIDE_LEVEL_BOUND'
  
  def __init__(self,key,game_obj1,game_obj2,contact_manifold):
    Action.__init__(self,key)
    
    self.game_obj1 = game_obj1
    self.game_obj2 = game_obj2
    self.contact_manifold = contact_manifold

  
  
  
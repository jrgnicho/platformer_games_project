from physics_platformer.state_machine import Action

class CollisionAction(Action):
  
  
  DELIVER_HIT = 'DELIVER_HIT'
  TAKE_HIT = 'TAKE_HIT'
  ACTION_BODY_COLLISION = 'ACTION_BODY_COLLISION'
  LEDGE_ACTION_COLLISION = 'LEDGE_ACTION_COLLISION'
  LEDGE_BOTTOM_COLLISION = 'LEDGE_BOTTOM_COLLISION'
  SURFACE_COLLISION = 'SURFACE_COLLISION'
  CEILING_COLLISION = 'CEILING_COLLISION'
  LEFT_WALL_COLLISION = 'LEFT_WALL_COLLISION'
  RIGHT_WALL_COLLISION = 'RIGHT_WALL_COLLISION'
  COLLIDE_LEVEL_BOUND = 'COLLIDE_LEVEL_BOUND'
  COLLISION_FREE = 'COLLISION_FREE'
  FREE_FALL = 'FREE_FALL'
  
  def __init__(self,key,game_obj1,game_obj2,contact_manifold):
    Action.__init__(self,key)
    
    self.game_obj1 = game_obj1
    self.game_obj2 = game_obj2
    self.contact_manifold = contact_manifold

  
  
  
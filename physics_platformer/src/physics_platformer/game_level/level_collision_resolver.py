from panda3d.core import Vec3
from panda3d.core import Mat4
from panda3d.core import TransformState
from panda3d.core import NodePath
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletWorld
from physics_platformer.game_level import Platform
from physics_platformer.collision import CollisionMasks
from physics_platformer.collision import CollisionResolver
from physics_platformer.game_actions import CollisionAction
from physics_platformer.collision import CollisionActionMatrix
from physics_platformer.game_object import GameObject
import logging

class LevelCollisionResolver(CollisionResolver):
  
  def __init__(self,physics_world):
    LevelCollisionResolver.__init__(self)
    
    self.free_falling_objects_ = {}
    
  def setupCollisionRules(self,physics_world):
    
    self.physics_world_ = physics_world
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_TOP.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_LEFT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_RIGHT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_AABB.getLowestOnBit(),CollisionMasks.LEVEL_BOUND.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_AABB.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.ACTION_BODY.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),True)
    
    # populating collision action matrix
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.SURFACE_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),CollisionAction.LEDGE_BOTTOM_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_TOP.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.CEILING_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_LEFT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.LEFT_WALL_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_RIGHT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.RIGHT_WALL_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.ACTION_BODY.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),CollisionAction.LEDGE_ACTION_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_AABB.getLowestOnBit(),CollisionMasks.LEVEL_BOUND.getLowestOnBit(),CollisionAction.COLLIDE_LEVEL_BOUND)
  
    logging.debug(str(self.collision_action_matrix_))
    
  def processCollisions(self,contact_manifolds, game_objects_dict, mobile_objects_names):
    
    # reset free falling dictionary
    self.free_falling_objects_ = dict.fromkeys(mobile_objects_names,True)
    
    for cm in contact_manifolds:
      
      node0 = cm.getNode0()
      node1 = cm.getNode1()
      col_mask1 = node0.getIntoCollideMask()
      col_mask2 = node1.getIntoCollideMask()
      
      key1 = node0.getPythonTag(GameObject.ID_PYTHON_TAG)
      key2 = node1.getPythonTag(GameObject.ID_PYTHON_TAG)
            
      obj1 = game_objects_dict[key1] if (key1 is not None and game_objects_dict.has_key(key1)) else None
      obj2 = game_objects_dict[key2] if (key2 is not None and game_objects_dict.has_key(key2)) else None      
      
      if (obj1 is not None) and self.collision_action_matrix_.hasEntry(
                                                                       col_mask1.getLowestOnBit() , 
                                                                       col_mask2.getLowestOnBit()):
        
        action_key = self.collision_action_matrix_.getAction(col_mask1.getLowestOnBit() , col_mask2.getLowestOnBit())
        action = CollisionAction(action_key,obj1,obj2,cm)            
        obj1.execute(action)
                
        # check for free falling
        if self.free_falling_objects_.has_key(key1) and col_mask1 == CollisionMasks.GAME_OBJECT_BOTTOM:
          self.free_falling_objects_[key1] = False
        
      if (obj2 is not None) and self.collision_action_matrix_.hasEntry(
                                                                       col_mask2.getLowestOnBit() ,
                                                                       col_mask1.getLowestOnBit()):
        
        action_key = self.collision_action_matrix_.getAction(col_mask2.getLowestOnBit() , col_mask1.getLowestOnBit())
        action = CollisionAction(action_key,obj2,obj1,cm)
        obj2.execute(action)
        
        # check for free falling
        if self.free_falling_objects_.has_key(key2) and col_mask2 == CollisionMasks.GAME_OBJECT_BOTTOM:
          self.free_falling_objects_[key2] = False
    
    
    # objects in free fall      
    for id,free_fall in self.free_falling_objects_.items():      
      if free_fall:
        obj = game_objects_dict[id]
        action = CollisionAction(CollisionAction.FREE_FALL,obj,None,None)
        obj.execute(action)
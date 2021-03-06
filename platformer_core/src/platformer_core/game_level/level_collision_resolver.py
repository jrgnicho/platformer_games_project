from panda3d.core import Vec3
from panda3d.core import Mat4
from panda3d.core import TransformState
from panda3d.core import NodePath
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletWorld
from platformer_core.game_level import Platform
from platformer_core.collision import CollisionMasks
from platformer_core.collision import CollisionResolver
from platformer_core.game_actions import CollisionAction
from platformer_core.collision import CollisionActionMatrix
from platformer_core.game_object import GameObject
import logging

class LevelCollisionResolver(CollisionResolver):
  
  def __init__(self):
    CollisionResolver.__init__(self)
    
  def setupCollisionRules(self,physics_world):
    
    self.physics_world_ = physics_world
    
    # setting collision rules
    #self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.PLATFORM_RIGID_BODY.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.SURFACE.getLowestOnBit(),True)
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_TOP.getLowestOnBit(),CollisionMasks.PLATFORM_RIGID_BODY.getLowestOnBit(),True)
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_LEFT.getLowestOnBit(),CollisionMasks.WALL.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_RIGHT.getLowestOnBit(),CollisionMasks.WALL.getLowestOnBit(),True)
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_RIGID_BODY.getLowestOnBit(),CollisionMasks.LEVEL_BOUND.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_RIGID_BODY.getLowestOnBit(),CollisionMasks.PLATFORM_RIGID_BODY.getLowestOnBit(),True)   
     
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.ACTION_TRIGGER_1.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),True)
    
    # populating collision action matrix
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.SURFACE.getLowestOnBit(),
                                           CollisionAction.SURFACE_COLLISION,CollisionAction.NONE)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),
                                           CollisionAction.LEDGE_BOTTOM_COLLISION,CollisionAction.NONE)
    
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_TOP.getLowestOnBit(),CollisionMasks.PLATFORM_RIGID_BODY.getLowestOnBit(),
                                           CollisionAction.CEILING_COLLISION,CollisionAction.NONE)
    
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_LEFT.getLowestOnBit(),CollisionMasks.WALL.getLowestOnBit(),
                                           CollisionAction.LEFT_WALL_COLLISION,CollisionAction.NONE)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_RIGHT.getLowestOnBit(),CollisionMasks.WALL.getLowestOnBit(),
                                           CollisionAction.RIGHT_WALL_COLLISION,CollisionAction.NONE)
    
    self.collision_action_matrix_.addEntry(CollisionMasks.ACTION_TRIGGER_1.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),
                                           CollisionAction.LEDGE_ACTION_COLLISION,CollisionAction.NONE)
    
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_RIGID_BODY.getLowestOnBit(),CollisionMasks.LEVEL_BOUND.getLowestOnBit(),
                                           CollisionAction.COLLIDE_LEVEL_BOUND,CollisionAction.NONE)
  
    logging.debug(str(self.collision_action_matrix_))
    
  def processCollisions(self,contact_manifolds, game_objects_dict, mobile_object_ids ):
    
    # reset free falling dictionary
    free_falling_dict = dict.fromkeys(mobile_object_ids,True)
    processed_contacts = []
    
    num_contacts = len(contact_manifolds)
    for i in range(0,num_contacts):
      
      cm = contact_manifolds[i]
      node0 = cm.getNode0()
      node1 = cm.getNode1()
      col_mask1 = node0.getIntoCollideMask()
      col_mask2 = node1.getIntoCollideMask()
      
      if not self.collision_action_matrix_.hasEntry(col_mask1.getLowestOnBit() , col_mask2.getLowestOnBit()): 
        continue
      
      key1 = node0.getName() 
      key2 = node1.getName() 
            
      # looking up game objects      
      obj1 = game_objects_dict[key1] if (key1 is not None and key1 in game_objects_dict) else None
      if obj1 is None:
        key1 = node0.getPythonTag(GameObject.ID_PYTHON_TAG)
        obj1 = game_objects_dict[key1] if (key1 is not None and key1 in game_objects_dict) else None
        
      obj2 = game_objects_dict[key2] if (key2 is not None and key2 in game_objects_dict) else None   
      if obj2 is None:
        key2 = node1.getPythonTag(GameObject.ID_PYTHON_TAG)
        obj2 = game_objects_dict[key2] if (key2 is not None and key2 in game_objects_dict) else None
      
      if obj1 is None:
        logging.warn("Found Unknown objects '%s' while resolving collisions"%(key1))
        continue
      
      if obj2 is None:
        logging.warn("Found Unknown objects '%s' while resolving collisions"%(key2))
        continue
       
      action_key1 , action_key2 = self.collision_action_matrix_.getActions(col_mask1.getLowestOnBit() , col_mask2.getLowestOnBit())      
      processed_contacts.append(i)
      
      if action_key1 != CollisionAction.NONE:
        action = CollisionAction(action_key1,obj1,obj2,cm)            
        obj1.execute(action)
                
      # check for free falling
      if key1 in free_falling_dict and col_mask1 == CollisionMasks.GAME_OBJECT_BOTTOM:
        free_falling_dict[key1] = False
        
      if  action_key2 != CollisionAction.NONE:
        action = CollisionAction(action_key2,obj2,obj1,cm)            
        obj2.execute(action)
        
      # check for free falling
      if key2 in free_falling_dict and col_mask2 == CollisionMasks.GAME_OBJECT_BOTTOM:
        free_falling_dict[key2] = False
    
    # objects in free fall      
    falling_objs_ids = [t[0] for t in list(free_falling_dict.items()) if t[1]]
    for id in falling_objs_ids:
      obj = game_objects_dict[id]
      action = CollisionAction(CollisionAction.FREE_FALL,obj,None,None)
      obj.execute(action)
      
    # removing processed contacts
    unprocessed_contacts = [contact_manifolds[i] for i in range(0,num_contacts) if processed_contacts.count(i) == 0]
    return unprocessed_contacts
      
    
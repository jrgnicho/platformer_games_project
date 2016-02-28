from physics_platformer.game_level import Platform
from physics_platformer.game_level import Sector, SectorTransition
from physics_platformer.collision import CollisionMasks
from physics_platformer.collision import CollisionResolver
from physics_platformer.game_actions import CollisionAction
from physics_platformer.collision import CollisionActionMatrix
from physics_platformer.game_object import GameObject
import logging

class LevelSectorResolver(CollisionResolver):
  
  def __init__(self,sectors_dict):
    CollisionResolver.__init__(self)
    self.sectors_dict_ = sectors_dict
    
  def setupCollisionRules(self,physics_world):
    
    self.physics_world_ = physics_world
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.SECTOR_TRANSITION.getLowestOnBit(),CollisionMasks.GAME_OBJECT_ORIGIN.getLowestOnBit(),True)
    
    # populating collision action matrix
    self.collision_action_matrix_.addEntry(CollisionMasks.SECTOR_TRANSITION.getLowestOnBit(),CollisionMasks.GAME_OBJECT_ORIGIN.getLowestOnBit(),
                                           CollisionAction.NONE,CollisionAction.NONE)

    
  def processCollisions(self,contact_manifolds, game_objects_dict, mobile_object_ids ):
    
    processed_contacts = []
    
    num_contacts = len(contact_manifolds)
    for i in range(0,num_contacts):
      
      cm = contact_manifolds[i]
      sector_transition_node = cm.getNode0()
      node1 = cm.getNode1()
      col_mask1 = sector_transition_node.getIntoCollideMask().getLowestOnBit()
      col_mask2 = node1.getIntoCollideMask().getLowestOnBit()
      
      if not self.collision_action_matrix.hasEntry(col_mask1,col_mask2):
        continue
      src_sector  = self.sectors_dict_[sector_transition_node.getPythonTag(SectorTransition.SOURCE_SECTOR_NAME)]
      dest_sector = self.sectors_dict_[sector_transition_node.getPythonTag(SectorTransition.DESTINATION_SECTOR_NAME)]
      id = node1.getPythonTag(GameObject.ID_PYTHON_TAG)
      obj = game_objects_dict.get(id,None)
      
      if obj is None:
        logging.warn('Object with game id %s was not found')
        continue
      
      src_sector.remove(obj)
      dest_sector.attach(obj)
      
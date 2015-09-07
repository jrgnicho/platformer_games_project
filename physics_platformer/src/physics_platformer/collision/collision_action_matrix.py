import logging
from physics_platformer.collision import *

class CollisionActionMatrix(object):
  
  def __init__(self):
    
    self.entries_ = {}
    
  def addEntry(self,col_mask1, col_mask2 , action_key):
    """
    addEntry(CollisionMask col_mask1,CollisionMask col_mask2, action action)
    Adds a collision entry pair along with its corresponding action
    """
    col_mask_entry_map = None
    if self.entries_.has_key(col_mask1):
      col_mask_entry_map = self.entries_[col_mask1]
    else:
      col_mask_entry_map = {} 
    
    
    col_mask_entry_map[col_mask2] = action_key
    
  
  def hasEntry(self,col_mask1,col_mask2):    
    """
    hasEntry(CollisionMask col_mask1, CollisionMask col_mask2)
    Returns True or False.  Checks that the requested entry pair has been added.
    """
    if self.entries_.has_key(col_mask1):
      map = self.entries_[col_mask1]
      if map.has_key(col_mask2):
        return True
      
    return False
  
  
  def getAction(self,col_mask1,col_mask2):
    
    if self.entries_.has_key(col_mask1):
      map = self.entries_[col_mask1]
      if map.has_key(col_mask2):
        return map[col_mask]
    
    logging.error("CollisionActionMatrix does not have requested collision pair") 
    return None
  
  def clear(self):    
    self.entries_.clear()
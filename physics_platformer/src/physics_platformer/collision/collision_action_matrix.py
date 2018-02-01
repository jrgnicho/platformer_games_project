import logging
from physics_platformer.collision import *

class CollisionActionMatrix(object):
  
  def __init__(self):
    
    self.entries_ = {}
    
  def addEntry(self,col_mask1, col_mask2 , action_key1, action_key2):
    """
    void addEntry(CollisionMask col_mask1,CollisionMask col_mask2, String action_key1, String action_key2)
    
      Adds a collision entry pair along with its corresponding action tuple.  The
      action_key1 will be applied to the first object while action_key2 will be
      applied to the second
    """
    col_mask_entry_map = None
    if col_mask1 in self.entries_:
      col_mask_entry_map = self.entries_[col_mask1]
    else:
      col_mask_entry_map = {} 
    
    
    col_mask_entry_map[col_mask2] = (action_key1,action_key2)
    self.entries_[col_mask1] = col_mask_entry_map
    
  
  def hasEntry(self,col_mask1,col_mask2):    
    """
    Bool hasEntry(CollisionMask col_mask1, CollisionMask col_mask2)
      Returns True or False.  Checks that the requested entry pair has been added.
    """
    try:
      if col_mask1 in self.entries_:
        map = self.entries_[col_mask1]
        if col_mask2 in map:
          return True
    except SystemError:
      logging.error("Key %s not found, but produced look up errors"%(str(col_mask1)))
      
    return False
  
  
  def getActions(self,col_mask1,col_mask2):
    """
    (String,String) getActions(CollisionMask col_mask1, CollisionMask col_mask2)
      Returns a tuple with the actions keys corresponding to this combination entry
    """
    
    if col_mask1 in self.entries_:
      map = self.entries_[col_mask1]
      if col_mask2 in map:
        return map[col_mask2]
    
    logging.error("CollisionActionMatrix does not have requested collision pair") 
    return None
  
  def clear(self):    
    self.entries_.clear()
    
  def __str__(self):
    stream = 'Collision Action Matrix\n'
    for k,map in list(self.entries_.items()):
      stream+= "\t%s : %s\n"%(str(k),str(map))
      
    return stream
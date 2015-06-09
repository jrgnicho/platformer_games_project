from physics_platformer.ssf import SFFLoader
from panda3d.core import CollisionBox
import logging

class AnimationDetails(object):
  
  def __init__(self):
    
    self.name = ''
    self.hit_boxes_ = []
    self.action_boxes_ = []
    self.images_ = []
    self.framerate_ = 0
    

class CharacterLoader(object):
  
  def __init__(self):
    """
    Loads Animation Actions from an AIR File created in Fighter Factor 3
    """
    
    self.anims_dict_ = {}
    
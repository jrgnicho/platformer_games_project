from panda3d.core import Vec3
from physics_platformer.state_machine import *

class CharacterStatus(object):
  
  def __init__(self):
    
    self.health = 100
    self.velocity = Vec3(0,0,0)
    self.platform = None # Latest platform that the character touched

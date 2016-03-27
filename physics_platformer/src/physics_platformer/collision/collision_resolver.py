from panda3d.core import Vec3
from panda3d.core import Mat4
from panda3d.core import TransformState
from panda3d.core import NodePath
from panda3d.bullet import BulletWorld
from physics_platformer.collision import CollisionMasks
from physics_platformer.game_actions import CollisionAction
from physics_platformer.collision import CollisionActionMatrix
import logging
import abc  # abstract base class

class CollisionResolver(object): 
  
  """
  This is an interface which provides methods for deciding how to deal with collisions between
  various objects in the game
  """
   
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    self.collision_action_matrix_ = CollisionActionMatrix()
  
  
  @abc.abstractmethod  
  def setupCollisionRules(self,physics_world):
    """
    Enables allowed collision groups and defines the actions triggered when the corresponding object 
    types collide
    """
    pass

  @abc.abstractmethod
  def processCollisions(self,contact_manifolds, game_objects_dict, mobile_objects_ids):
    """
    Processes the relevant contact manifolds
    processCollisions(ContactManifolds contact_manifolds, Dict{tring,GameObjects} game_objects_dict, String[] mobile_object_names)
    """
    pass
  
  
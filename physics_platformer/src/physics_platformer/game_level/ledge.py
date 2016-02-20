from panda3d.core import Vec3
from panda3d.bullet import BulletGhostNode
from panda3d.bullet import BulletBoxShape
from panda3d.core import NodePath
from physics_platformer.game_object import GameObject
from physics_platformer.collision import *


class Ledge(GameObject):
  
  __SIDE_LENGTH__ = 0.1
  __DEFAULT_SIZE__ = Vec3(__SIDE_LENGTH__,1,__SIDE_LENGTH__)
  
  def __init__(self,name,right_side_ledge, parent_platform , size = __DEFAULT_SIZE__):
    '''
    Ledge(string name,Bool right_side_ledge, Platform parent_platform, Vec3 size = default)
    
      Creates a ledge object used to detect the extent of a platform at a given location
    '''
    mass = 0
    setup_visual = False
    GameObject.__init__(self,name,size,mass,setup_visual)
    
    # storing members
    self.parent_platform_ = parent_platform
    self.is_right_side_ledge_ = right_side_ledge

    # half dimensions
    half_width = 0.5*size.getX()
    half_height = 0.5*size.getZ()
    half_depth = 0.5*size.getY()
    
    ledge_gn = BulletGhostNode(name)
    ledge_gn.addShape(BulletBoxShape(Vec3(half_width,half_depth,half_height)) )
    ledge_gn.setIntoCollideMask(CollisionMasks.LEDGE)  
    
    # This is hackish but don't know of a different way to replace the BulletRigidBody with a BulletGhostNode
    self.clear()
    NodePath.__init__(self,ledge_gn)
    
  def isRightSideLedge(self):
    '''
    Returns true if the platform inmediate surface ends on the right, False otherwise
    '''
    return self.is_right_side_ledge_
  
  def getParentPlatform(self):
    return self.parent_platform_
    
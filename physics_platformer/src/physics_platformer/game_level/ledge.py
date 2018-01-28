from panda3d.core import Vec2
#from panda3d.bullet import BulletUpAxis
from panda3d.bullet import BulletGhostNode, BulletCylinderShape,\
  getDefaultUpAxis, Y_up
from panda3d.bullet import BulletBoxShape
from panda3d.core import NodePath
from physics_platformer.game_object import GameObject
from physics_platformer.collision import *


class Ledge(GameObject):
  
  __RADIUS__ = 0.1
  __DEFAULT_SIZE__ = Vec3(2*__RADIUS__,1,0)
  
  def __init__(self,name,right_side_ledge, parent_platform , size = __DEFAULT_SIZE__):
    '''
    Ledge(string name,Bool right_side_ledge, Platform parent_platform, Vec3 size = default)
    
      Creates a ledge object used to detect the extent of a platform at a given location
      The size should be [diameter, height, 0] and the cylinder shape axis is oriented
      in the Y+ direction.
    '''
    
    # storing members
    radius = size.getX()*0.5
    height = size.getY();
    self.size_ = size
    self.parent_platform_ = parent_platform
    self.is_right_side_ledge_ = right_side_ledge

    
    ledge_gn = BulletGhostNode(name)
    ledge_gn.addShape(BulletCylinderShape(radius,height, Y_up) )
    #ledge_gn.getShape(0).setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
    ledge_gn.setIntoCollideMask(CollisionMasks.LEDGE)  
    
    GameObject.__init__(self,ledge_gn)
    
  def isRightSideLedge(self):
    '''
    Returns true if the platform inmediate surface ends on the right, False otherwise
    '''
    return self.is_right_side_ledge_
  
  def getParentPlatform(self):
    return self.parent_platform_
    
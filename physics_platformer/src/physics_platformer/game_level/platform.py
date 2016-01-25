from panda3d.core import Vec3, LPoint3, NodePath
from panda3d.core import TexturePool
from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletGhostNode
from physics_platformer.game_object import GameObject
from physics_platformer.game_level import Ledge
from physics_platformer.collision import *

class Platform(GameObject):
  
  __PERIMETER_THICKNESS__ = 0.2
  __LEDGE_BOX_SIDE_LENGHT = 0.1
  __PADDING__ = 0.1
  __DEFAULT_TEXTURE__ = TexturePool.loadTexture(GameObject.DEFAULT_RESOURCES_DIRECTORY +'/models/iron.jpg')
  
  def __init__(self,name,size,right_side_ledge = True, left_side_ledge = True):
    '''
    Platform(String name, Vec3 size, Bool right_side_ledge, Bool left_side_ledge)
    '''
    GameObject.__init__(self,name,size,0)
    self.setCollideMask(CollisionMasks.LEVEL_OBSTACLE)
    self.visual_nh_.setTexture(Platform.__DEFAULT_TEXTURE__,1) 
    
    # platform_ledge members
    self.left_ledge_ = Ledge(name + 'left-ledge',False,self) if left_side_ledge else None
    self.right_ledge_ = Ledge(name + 'right-ledge',True,self) if right_side_ledge else None
    self.ledges_ = [] # to avoid recreating this list 
    
    # ledge placement
    half_width = 0.5*size.getX()
    half_height = 0.5*size.getZ()
    half_depth = 0.5*size.getY()
    
    if left_side_ledge:
      self.left_ledge_.reparentTo(self)
      self.left_ledge_.setPos(Vec3(-half_width ,0,half_height))
      self.ledges_.append(self.left_ledge_)
      
    if right_side_ledge:
      self.right_ledge_.reparentTo(self)
      self.right_ledge_.setPos(Vec3(half_width ,0,half_height))
      self.ledges_.append(self.right_ledge_)
          
  def setPhysicsWorld(self,physics_world): 
    GameObject.setPhysicsWorld(self,physics_world)    
    for ledge in self.ledges_:
      self.physics_world_.attach(ledge.node())
      
      
  def clearPhysicsWorld(self):
    for ledge in self.ledges_:
      self.physics_world_.remove(ledge.node())
    GameObject.clearPhysicsWorld(self)
    
  def getChildrenGameObjects(self):
    return self.ledges_
    
  def getLeftLedge(self):
    '''
    Returns the NodePath to the left ledge BulletGhost node
    '''
    return self.left_ledge_
  
  def getRightLedge(self):
    '''
    Returns the NodePath to the right ledge BulletGhost node
    '''
    return self.right_ledge_
      
    
from panda3d.core import Vec3, LPoint3, NodePath
from panda3d.core import TexturePool
from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode
from panda3d.bullet import BulletGhostNode
from physics_platformer.game_object import GameObject
from physics_platformer.game_level import Ledge
from physics_platformer.game_level import Platform
from physics_platformer.collision import *

class SimplePlatform(Platform):
  
  __PERIMETER_THICKNESS__ = 0.1
  __LEDGE_BOX_SIDE_LENGHT__ = 0.2
  #__PADDING__ = 0.1
  __DEFAULT_TEXTURE__ = TexturePool.loadTexture(GameObject.DEFAULT_RESOURCES_DIRECTORY +'/models/iron.jpg')
  
  def __init__(self,name,size,right_side_ledge = True, left_side_ledge = True):
    '''
    Creates a box shaped platform
    SimplePlatform(String name, Vec3 size, Bool right_side_ledge, Bool left_side_ledge)
    '''
    
    # creating a static box
    collision_shape = BulletBoxShape(size/2) 
    collision_shape.setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
    bt_node = BulletRigidBodyNode(name)
    bt_node.addShape(collision_shape)
    bt_node.setMass(0)
    
    # calling super constructor
    super(SimplePlatform,self).__init__(bt_node)
    self.size_ = size
    self.setCollideMask(CollisionMasks.PLATFORM_RIGID_BODY)
    visual_np = GameObject.createSimpleBoxVisualNode(self,self.size_, self.getName() + '-visual')
    visual_np.setTexture(SimplePlatform.__DEFAULT_TEXTURE__,1) 
    
    # addding ledges
    ledge_size = Vec3(SimplePlatform.__LEDGE_BOX_SIDE_LENGHT__,self.getSize().getY(),SimplePlatform.__LEDGE_BOX_SIDE_LENGHT__)
    self.left_ledge_ = Ledge(name + 'left-ledge',False,self,ledge_size) if left_side_ledge else None
    self.right_ledge_ = Ledge(name + 'right-ledge',True,self,ledge_size) if right_side_ledge else None
    self.ledges_ = [] 
    
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
      
    # creating platform floor node
    thickness = SimplePlatform.__PERIMETER_THICKNESS__
    self.floor_ghost_np_ = self.attachNewNode(BulletGhostNode(name + 'floor'))    
    self.floor_ghost_np_.node().addShape(BulletBoxShape(Vec3((size.getX()-2*thickness)*0.5,size.getY()*0.5 ,thickness*0.5) ))
    #self.floor_ghost_np_.node().getShape(0).setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
    self.floor_ghost_np_.setPosHpr(self,Vec3(0,0,(size.getZ() - thickness)*0.5),Vec3.zero())
    self.floor_ghost_np_.node().setIntoCollideMask(CollisionMasks.SURFACE)
    
    # creating platform right wall node
    self.rightwall_ghost_np_ = self.attachNewNode(BulletGhostNode(name + 'right-wall'))
    self.rightwall_ghost_np_.node().addShape(BulletBoxShape(Vec3(thickness*0.5,size.getY()*0.5,size.getZ()*0.5 )))
    #self.rightwall_ghost_np_.node().getShape(0).setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
    self.rightwall_ghost_np_.setPosHpr(self,Vec3((size.getX() - thickness)*0.5,0,0),Vec3.zero())
    self.rightwall_ghost_np_.node().setIntoCollideMask(CollisionMasks.WALL)
    
    # creating platform left wall node
    self.leftwall_ghost_np_ = self.attachNewNode(BulletGhostNode(name + 'left-wall'))
    self.leftwall_ghost_np_.node().addShape(BulletBoxShape(Vec3(thickness*0.5,size.getY()*0.5,size.getZ()*0.5 )))
    #self.leftwall_ghost_np_.node().getShape(0).setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
    self.leftwall_ghost_np_.setPosHpr(self,Vec3(-(size.getX() - thickness)*0.5,0,0),Vec3.zero())
    self.leftwall_ghost_np_.node().setIntoCollideMask(CollisionMasks.WALL)
    
    # storing all ghost nodes in subclass list
    self.bt_children_nodes_ = [self.leftwall_ghost_np_, self.rightwall_ghost_np_, self.floor_ghost_np_]
    
    # setting id 
    self.setObjectID(self.getName())
    
    
  def getLeftLedge(self):
    '''
    Returns the left Ledge object
    '''
    return self.left_ledge_
  
  def getRightLedge(self):
    '''
    Returns the right Ledge object
    '''
    return self.right_ledge_
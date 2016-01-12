from panda3d.core import Vec3, LPoint3, NodePath
from panda3d.core import TexturePool
from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletGhostNode
from physics_platformer.game_object import GameObject
from physics_platformer.collision import *

class Platform(GameObject):
  
  __PERIMETER_THICKNESS__ = 0.2
  __LEDGE_BOX_SIDE_LENGHT = 0.1
  __PADDING__ = 0.1
  __DEFAULT_TEXTURE__ = TexturePool.loadTexture(GameObject.DEFAULT_RESOURCES_DIRECTORY +'/models/iron.jpg')
  
  def __init__(self,name,size):
    GameObject.__init__(self,name,size,0)
    self.setCollideMask(CollisionMasks.LEVEL_OBSTACLE)
    self.visual_nh_.setTexture(Platform.__DEFAULT_TEXTURE__,1) 
    
    # creating Bullet Ghost boxes around the perimeter 
    width = size.getX()
    height = size.getZ()
    depth = size.getY()
    
    # half dimensions
    half_width = 0.5*width
    half_height = 0.5*height
    half_depth = 0.5*depth
    self.ghost_nodes_ = []
    
    # creating ledges
    half_side_lenght = 0.5*Platform.__LEDGE_BOX_SIDE_LENGHT
    
    left_ledge = BulletGhostNode('ledge-left')
    transform = TransformState.makePos(Vec3(-half_width ,0,half_height))
    left_ledge.addShape(BulletBoxShape(Vec3(half_side_lenght,half_depth,half_side_lenght)) )
    left_ledge.setIntoCollideMask(CollisionMasks.LEDGE)    
    left_ledge_np = self.attachNewNode(left_ledge)
    left_ledge_np.setTransform(self,transform)
    self.ghost_nodes_.append(left_ledge_np)
    
    right_ledge = BulletGhostNode('ledge-right')
    transform = TransformState.makePos(Vec3(half_width ,0,half_height))
    right_ledge.addShape(BulletBoxShape(Vec3(half_side_lenght,half_depth,half_side_lenght)))
    right_ledge.setIntoCollideMask(CollisionMasks.LEDGE)    
    right_ledge_np = self.attachNewNode(right_ledge)
    right_ledge_np.setTransform(self,transform)
    self.ghost_nodes_.append(right_ledge_np)
          
  def setObjectID(self,id):
    GameObject.setObjectID(self,id)
    for gh in self.ghost_nodes_:
      gh.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
      
  def setPhysicsWorld(self,physics_world): 
    GameObject.setPhysicsWorld(self,physics_world)
    
    for gn in self.ghost_nodes_:
      self.physics_world_.attach(gn.node())
      
  def clearPhysicsWorld(self):
    for gn in self.ghost_nodes_:
      self.physics_world_.remove(gn.node())
    GameObject.clearPhysicsWorld(self)
    
  def getLeftLedge(self):
    '''
    Returns the NodePath to the left ledge BulletGhost node
    '''
    return self.ghost_nodes_[0]
  
  def getRightLedge(self):
    '''
    Returns the NodePath to the right ledge BulletGhost node
    '''
    return self.ghost_nodes_[1]
      
    
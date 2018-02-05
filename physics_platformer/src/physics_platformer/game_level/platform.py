from panda3d.core import Vec3, LPoint3, NodePath
from panda3d.core import TexturePool
from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape, BulletBodyNode
from panda3d.bullet import BulletGhostNode
from physics_platformer.game_object import GameObject
from physics_platformer.game_level import Ledge
from physics_platformer.collision import *
import logging

class Platform(GameObject):  

  
  def __init__(self,bt_rigid_body):
    '''
    Platform(BulletRigidBody bn)
    '''
    GameObject.__init__(self,bt_rigid_body)    
    self.setCollideMask(CollisionMasks.PLATFORM_RIGID_BODY)
    
    self.ledges_ = [] 
    self.bt_children_nodes_ = [] # Includes walls, surfaces and ceilings
    
    # setting id 
    self.setObjectID(self.getName())
    
    
  def addLedge(self,ledge, pos = Vec3.zero()):
    
    if type(ledge) is not Ledge:
      logging.error("Object is not a Ledge instance")
      return False
    
    ledge.reparentTo(self)
    ledge.setPos(pos)
    self.ledges_.append(ledge)
    
    return True
    
  def addFeatureNode(self,feature_node, transform_st = TransformState.makeIdentity()):
    """
    Adds a BulletBodyNode subclass that is a feature of the platform such as wall, surface or ceiling
    The feature type is set with the setintoCollideMask method of the node and should be set to the corresponding
    CollisionMask
    """
    if not isinstance(feature_node, BulletBodyNode):
      logging.error("Object must be a subclass of BulletBodyNode")
      return False
    
    np = self.attachNewNode(feature_node)
    np.setTransform(transform_st)
    self.bt_children_nodes_.append(np)
    
    return True
    
  def setObjectID(self,id):            
    self.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
    nps = self.getChildren()
    for np in self.bt_children_nodes_:
      np.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
          
  def setPhysicsWorld(self,physics_world): 
    GameObject.setPhysicsWorld(self,physics_world)    
    for ledge in self.ledges_:
      self.physics_world_.attach(ledge.node())
      
    for child in self.bt_children_nodes_:
      self.physics_world_.attach(child.node())
      
      
  def clearPhysicsWorld(self):
    for ledge in self.ledges_:
      self.physics_world_.remove(ledge.node())
      
    for child in self.bt_children_nodes_:
      self.physics_world_.remove(child.node())
      
    GameObject.clearPhysicsWorld(self)
    
  def getChildrenGameObjects(self):
    return self.ledges_   

      
    
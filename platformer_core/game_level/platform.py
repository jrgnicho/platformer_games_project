from panda3d.core import Vec3, LPoint3, NodePath
from panda3d.core import TexturePool
from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape, BulletBodyNode
from panda3d.bullet import BulletGhostNode
from platformer_core.game_object import GameObject
from platformer_core.game_level import Ledge
from platformer_core.collision import *
import logging

class Platform(GameObject):  

  
  def __init__(self,bt_rigid_body):
    '''
    Platform(BulletRigidBody bn)
    '''
    GameObject.__init__(self,bt_rigid_body)    
    self.setCollideMask(CollisionMasks.PLATFORM_RIGID_BODY)
    
    self.ledges_ = [] 
    
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
   
  def setObjectID(self,id):            
    self.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
    
    nps = self.getChildren()
    for child in nps:
      if not isinstance(child.node(), BulletBodyNode):
        continue  
      child.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
          
  def setPhysicsWorld(self,physics_world): 
    GameObject.setPhysicsWorld(self,physics_world)    
    
    nps = self.getChildren()  
    for child in nps:
      if not isinstance(child.node(), BulletBodyNode):
        continue  
      self.physics_world_.attach(child.node())
      
      
  def clearPhysicsWorld(self):
      
    nps = self.getChildren()  
    for child in nps:
      if not isinstance(child.node(), BulletBodyNode):
        continue      
      self.physics_world_.remove(child.node())
      
    GameObject.clearPhysicsWorld(self)
    
  def getChildrenGameObjects(self):
    return self.ledges_   
  

      
    
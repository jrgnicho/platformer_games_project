import logging
from pathlib import Path

from panda3d.core import ModelPool
from panda3d.core import TexturePool

from panda3d.core import TexturePool
from panda3d.core import LColor
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import LPoint3
from panda3d.core import BoundingVolume
from panda3d.core import BoundingBox

from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletConvexHullShape
from panda3d.bullet import BulletBodyNode
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletWorld
from direct.showbase.ShowBase import ShowBase

from platformer_core.collision import *
from platformer_core.state_machine import Action

from platformer_core.resource_management.assets_common import AssetsLocator

"""
Game Object class

"""
class GameObject(NodePath):
  
    DEFAULT_RESOURCES_DIRECTORY = str(Path(AssetsLocator.get_simple_assets_path()))   
    DEFAULT_TEXTURE = TexturePool.loadTexture(DEFAULT_RESOURCES_DIRECTORY +'/models/limba.jpg')
    DEFAULT_BOX_MODEL = NodePath(ModelPool.loadModel( DEFAULT_RESOURCES_DIRECTORY + '/models/box.egg'))
    
    ID_PYTHON_TAG = "ObjectID"
    DEFAULT_COLLISION_MARGIN = 0.01
    ORIGIN_SPHERE_RADIUS = 0.05
    ORIGIN_XOFFSET = 0.5
    
    
    def __init__(self,*args):   
      """
      Creates an empty game object
      
      GameObject(string name)
      
      GameObject(BulletBodyNode bn)
          
          Inherits from panda3d.core.NodePath
      
      """
      name = ''
      bn = None
      if len(args) > 0:
        if isinstance(args[0],str):
          name = args[0]          
          NodePath.__init__(self,PandaNode(name))
        elif isinstance(args[0], BulletBodyNode):
          bn = args[0]
          NodePath.__init__(self,bn)
        else:
          raise ValueError('Invalid argument for GameObject')
      
      # instantiating to a bullet rigid body
      self.physics_world_ = None
      self.size_ = self.__estimateSize__()
      GameObject.setObjectID(self, self.getName())
    

        
    @classmethod        
    def createBox(cls,name,size,mass = 0,setup_visual = True):
    
      """
      Creates a game object and initializes it to a box
      
      GameObject.createBox(string name,
          Vec3 size,
          float mass,
          Bool setup_visual)
          
          Inherits from panda3d.core.NodePath
      """
      box = cls(name)
      box.__initToBox__(name,size,mass,setup_visual)
      return box;
    
    def __initToBox__(self,name, size,mass = 0,add_visual = True):
      
      NodePath.__init__(self,BulletRigidBodyNode(name))
      
      self.physics_world_ = None
      
      # size
      self.size_ = size        
      
      # set collision shape
      collision_shape = BulletBoxShape(self.size_/2) 
      collision_shape.setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
      self.node().addShape(collision_shape)
      self.node().setMass(mass)
      self.setCollideMask(CollisionMasks.GAME_OBJECT_RIGID_BODY)
      
      #  setting bounding volume
      min_point = LPoint3(-0.5*size.getX(),-0.5*size.getY(),-0.5*size.getZ())
      max_point = LPoint3(0.5*size.getX(),0.5*size.getY(),0.5*size.getZ())
      self.node().setBoundsType(BoundingVolume.BT_box)    
      self.node().setBounds(BoundingBox(min_point ,max_point ))
      
      # Frame of reference
      self.reference_np_ = None      
      
      # visual properties
      if add_visual:     
            visual_np = GameObject.createSimpleBoxVisualNode(self,self.size_, self.getName() + '-visual')       
          
      # setting ID
      GameObject.setObjectID(self, self.getName())
             
    def setPhysicsWorld(self,physics_world): 
      if type(physics_world) is not BulletWorld:
        logging.error( "Object is not of type %s, skipping"%(str(type(BulletWorld))) )
        return
      
      if not isinstance(self.node() ,BulletBodyNode):
        logging.warn('The node is not a Bullet Node Type, not adding to Physics world')
        return
      
      if physics_world is self.physics_world_:
        return
              
      self.physics_world_ = physics_world
      self.physics_world_.attach(self.node())
      
    def getPhysicsWorld(self):
      return self.physics_world_
      
    def clearPhysicsWorld(self):
      if self.physics_world_ is not None:
        logging.debug('Removing %s from physics world'%(self.getName()))
        self.physics_world_.remove(self.node())
        
      self.physics_world_ = None
      
    def setObjectID(self,id):            
      self.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
      nps = self.getChildren()
      for np in nps:
        np.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
        
    def getObjectID(self):      
      return self.getPythonTag(GameObject.ID_PYTHON_TAG)
    
    def setReferenceNodePath(self,ref_np):
      '''
      setReferenceNodePath(Nodepath ref_np)
      
        Movement and Transform changes will be done relative to the ref_np Nodepath
      '''
      self.reference_np_ = ref_np     
      
    def getReferenceNodePath(self):  
      return self.reference_np_
       
    def getSize(self):
      '''
      Return Vec3 with the size of the objects
      '''
      return self.size_
    
    def getTop(self, ref_np = None):   
      z = self.getZ() if ref_np is None else self.getZ(ref_np)
         
      return (z + self.getSize().getZ()*0.5)
    
    def getBottom(self, ref_np = None):
      z = self.getZ() if (ref_np is None) else self.getZ(ref_np)
      return (z - self.getSize().getZ()*0.5)
    
    def getLeft(self, ref_np = None):
      x = self.getX() if (ref_np is None) else self.getX(ref_np)
      return (x - self.getSize().getX()*0.5)
    
    def getRight(self, ref_np = None):
      x = self.getX() if (ref_np is None) else self.getX(ref_np)
      return (x + self.getSize().getX()*0.5)    
            
    def getMax(self):
      '''
      LPoint3 Max in local coordinates
      '''
      return self.node().getInternalBounds().getMax() + self.getPos()
    
    def getMin(self):
      '''
      LPoint3 Min in local coordinates
      '''
      return self.node().getInternalBounds().getMin() + self.getPos()
    
    def getRigidBody(self):
      return self
      
    def execute(self,action):
      pass    
            
    def update(self,dt):
      pass
    
    def getChildrenGameObjects(self):
      return []

      
    def __estimateSize__(self):
      minp = LPoint3.zero()
      maxp = LPoint3.zero()
      size = Vec3.zero()
      if self.calcTightBounds(minp,maxp):
        size = maxp - minp
        
      return size 
    
    
    @staticmethod
    def createSimpleBoxVisualNode(parent_np, size, name):
      """
      Convenience function that returns a Nodepath containing a textured box
      """      
      template_np = GameObject.DEFAULT_BOX_MODEL 
      template_np.clearModelNodes()            
      box_np = template_np.instanceUnderNode(parent_np,name);  
      box_np.setTexture(GameObject.DEFAULT_TEXTURE,1)   
      
      if GameObject.DEFAULT_TEXTURE == None:
          logging.error('Texture failed to load')
      
      # scaling visual model to size
      bounds = box_np.getTightBounds()
      extents = Vec3(bounds[1] - bounds[0])
      scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
      box_np.setScale( size.getX()*scale_factor, size.getY()*scale_factor, size.getZ()*scale_factor)
      return box_np
    
        
        
        
    
    
    
        
        
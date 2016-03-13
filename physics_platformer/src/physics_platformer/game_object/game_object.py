import rospkg
import logging
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
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletWorld
from direct.showbase.ShowBase import ShowBase

from physics_platformer.collision import *
from physics_platformer.state_machine import Action

"""
Game Object class

"""
class GameObject(NodePath):
  
    DEFAULT_RESOURCES_DIRECTORY = rospkg.RosPack().get_path('physics_platformer') + '/resources'        
    DEFAULT_TEXTURE = TexturePool.loadTexture(DEFAULT_RESOURCES_DIRECTORY +'/models/limba.jpg')
    DEFAULT_BOX_MODEL = NodePath(ModelPool.loadModel( DEFAULT_RESOURCES_DIRECTORY + '/models/box.egg'))
    
    ID_PYTHON_TAG = "ObjectID"
    ORIGIN_SPHERE_RADIUS = 0.1
    DEFAULT_COLLISION_MARGIN = 0.01
    
    
    def __init__(self,name,size,mass = 0,setup_visual = True):   
        """
        GameObject(string name,
            Vec3 size,
            float mass,
            Bool setup_visual)
            
            Inherits from panda3d.core.NodePath
        
        """ 
        
        # instantiating to a bullet rigid body
        NodePath.__init__(self,BulletRigidBodyNode(name ))
        self.physics_world_ = None
        
        # size
        self.size_ = size        
        
        # set collision shape
        collision_shape = BulletBoxShape(self.size_/2) 
        collision_shape.setMargin(GameObject.DEFAULT_COLLISION_MARGIN)
        self.node().addShape(collision_shape)
        self.node().setMass(mass)
        self.setCollideMask(CollisionMasks.GAME_OBJECT_AABB)
        
        #  setting bounding volume
        min_point = LPoint3(-0.5*size.getX(),-0.5*size.getY(),-0.5*size.getZ())
        max_point = LPoint3(0.5*size.getX(),0.5*size.getY(),0.5*size.getZ())
        self.node().setBoundsType(BoundingVolume.BT_box)    
        self.node().setBounds(BoundingBox(min_point ,max_point ))
        
        # Frame of reference
        self.reference_np_ = None
        
        # visual properties
        if setup_visual:     
                   
            visual_nh = GameObject.DEFAULT_BOX_MODEL 
            visual_nh.clearModelNodes()            
            self.visual_nh_ = visual_nh.instanceUnderNode(self,name + '-visual');  
            self.visual_nh_.setTexture(GameObject.DEFAULT_TEXTURE,1)   
            
            if GameObject.DEFAULT_TEXTURE == None:
                logging.error('Texture failed to load')
            
            # scaling visual model
            bounds = self.visual_nh_.getTightBounds()
            extents = Vec3(bounds[1] - bounds[0])
            scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
            self.visual_nh_.setScale(self.size_.getX()*scale_factor,self.size_.getY()*scale_factor,self.size_.getZ()*scale_factor)
        else:
            self.visual_nh_ = NodePath() # create empty node
             
    def setPhysicsWorld(self,physics_world): 
      if type(physics_world) is not BulletWorld:
        logging.error( "Object is not of type %s"%(str(type(BulletWorld))) )
        
      self.physics_world_ = physics_world
      self.physics_world_.attach(self.node())
      
    def getPhysicsWorld(self):
      return self.physics_world_
      
    def clearPhysicsWorld(self):
      if self.physics_world_ is not None:
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

      
      
    
        
        
        
    
    
    
        
        
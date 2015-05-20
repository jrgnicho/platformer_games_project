
from direct.showbase import Loader

from panda3d.core import TexturePool
from panda3d.core import LColor
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode

from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletConvexHullShape
from panda3d.bullet import BulletRigidBodyNode

"""
Game Object class

"""
class GameObject(NodePath):
    DEFAULT_RESOURCES_DIRECTORY = 'resources/default'
    
    DEFAULT_BOX_MODEL = Loader.loadModel( GameObject.DEFAULT_RESOURCES_DIRECTORY + '/models/defaultbox.egg')
    DEFAULT_TEXTURE = TexturePool.loadTexture(GameObject.DEFAULT_RESOURCES_DIRECTORY +'/images/irong.jpg')
    
    def __init__(self,name,size,mass, bt_collision_shape = None ,use_visual = True,visual = None):    
        
        # instantiating to a bullet rigid body
        NodePath.__init__(self,BulletRigidBodyNode(name + "-rigid-body"))
        
        # size
        self.size_ = size        
        
        # set collision shape
        collision_shape = bt_collision_shape if bt_collision_shape != None else BulletBoxShape(Vec3(size[0],size[1],size[2])/2) 
        self.node().addShape(collision_shape)
        self.node().setMass(mass)
        self.node().setLinearFactor((1,0,1))   
        self.node().setAngularFactor((0,0,0))   
        self.setCollideMask(BitMask32().allOn())
        
        # set visual
        if use_visual:
            visual_nh
            if visual == None:
                visual_nh = GameObject.DEFAULT_BOX_MODEL
                visual_nh.setTexture(GameObject.DEFAULT_TEXTURE)
            else:
                visual_nh = visual
                
            self.visual_nh_ = visual_nh.instanceUnderNode(self,name + '-visual');
        else:
            self.visual_nh_ = NodePath() # create empty node
            
    def update(self,dt):
        pass
    
        
        
        
    
    
    
        
        
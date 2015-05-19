
from direct.showbase import Loader

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
    DEFAULT_BOX_MODEL = Loader.loadModel('models/box.egg')
    
    def __init__(self,name,size,mass, bt_collision_shape = None ,visual = None):    
        
        # instantiating to a bullet rigid body
        NodePath.__init__(self,BulletRigidBodyNode(name + "-rigid-body"))
        
        # size
        self.size_ = size        
        
        # set collision shape
        collision_shape = collision_shape if collision_shape != None else self.createBoxShape(size)        
        
        # set visual
        self.visual_nh_ = GameObject.DEFAULT_BOX_MODEL
        
        
    def createBoxShape(self,size):
        pass
    
    
    
        
        
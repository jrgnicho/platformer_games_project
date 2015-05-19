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
    
    def __init__(self,size,mass, collision_shape = None ,visual = None):
    
        NodePath.__init__(self)
        self.size_ = size
        
        # set collision shape
        self.collision_shape_ = collision_shape if collision_shape != None else self.createBoxShape(size)
        
        # set visual
        
        
    def createBoxShape(self,size):
        pass
    
    def createBoxVisual(self,size):
        pass
        
        
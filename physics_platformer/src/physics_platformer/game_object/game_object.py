import rospkg
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

from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletConvexHullShape
from panda3d.bullet import BulletRigidBodyNode
from direct.showbase.ShowBase import ShowBase

"""
Game Object class

"""
class GameObject(NodePath):
    DEFAULT_RESOURCES_DIRECTORY = rospkg.RosPack().get_path('physics_platformer') + '/resources'        
    DEFAULT_TEXTURE = TexturePool.loadTexture(DEFAULT_RESOURCES_DIRECTORY +'/models/limba.jpg')
    DEFAULT_BOX_MODEL = NodePath(ModelPool.loadModel( DEFAULT_RESOURCES_DIRECTORY + '/models/box.egg'))
    
    
    def __init__(self,name,size,mass = 0,setup_visual = True):   
        """
        GameObject(string name,
            Vec3 size,
            float mass,
            Bool setup_visual)
            
            Inherits from panda3d.core.NodePath
        
        """ 
        
        # instantiating to a bullet rigid body
        NodePath.__init__(self,name)
        self.rigid_body_np_ = NodePath(BulletRigidBodyNode(name + "-rigid-body"))
        
        # size
        self.size_ = size        
        
        # set collision shape
        collision_shape = BulletBoxShape(self.size_/2) 
        self.rigid_body_np_.node().addShape(collision_shape)
        self.rigid_body_np_.node().setMass(mass)
        self.rigid_body_np_.node().setLinearFactor((1,0,1))   
        self.rigid_body_np_.node().setAngularFactor((0,1,0))   
        self.rigid_body_np_.setCollideMask(BitMask32().allOn())
        
        # set visual
        if setup_visual:     
                   
            visual_nh = GameObject.DEFAULT_BOX_MODEL 
            visual_nh.clearModelNodes()            
            self.visual_nh_ = visual_nh.instanceUnderNode(self,name + '-visual');    
            #self.visual_nh_ = visual_nh.instanceTo(self);          
            self.visual_nh_.setTexture(GameObject.DEFAULT_TEXTURE,1)   
            
            if GameObject.DEFAULT_TEXTURE == None:
                print 'ERROR: Texture failed to load'
            
            # scaling visual model
            bounds = self.visual_nh_.getTightBounds()
            extents = Vec3(bounds[1] - bounds[0])
            scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
            self.visual_nh_.setScale(self.size_.getX()*scale_factor,self.size_.getY()*scale_factor,self.size_.getZ()*scale_factor)
        else:
            self.visual_nh_ = NodePath() # create empty node
            
        self.reparentTo(self.rigid_body_np_)
    
    def getSize(self):
        return self.size_
            
    def update(self,dt):
        pass
    
    def getRigidBody(self):
        return self.rigid_body_np_
    
        
        
        
    
    
    
        
        
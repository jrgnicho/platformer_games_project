#!/usr/bin/env python
from direct.interval.Interval import Interval
from physics_platformer.test import TestApplication
from physics_platformer.game_object import *
from physics_platformer.sprite import *
import rospkg
from direct.interval.LerpInterval import LerpFunc
from direct.interval.FunctionInterval import Func
from direct.interval.IntervalGlobal import Sequence
import sys
import logging
import getopt
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletGhostNode
from panda3d.bullet import BulletHingeConstraint
from panda3d.bullet import BulletBoxShape
from panda3d.core import TransformState

BOX_SIDE_LENGTH = 0.4

class TestHingeConstraint(TestApplication):
  
  def __init__(self):
    
    TestApplication.__init__(self)
    
  def setupPhysics(self):
    
    TestApplication.setupPhysics(self)
    
    # create box rigid body
    box_rigid_body = self.world_node_.attachNewNode(BulletRigidBodyNode("Box"))
    box_rigid_body.node().addShape(BulletBoxShape(Vec3(0.5 * BOX_SIDE_LENGTH,0.5 * BOX_SIDE_LENGTH,0.5 * BOX_SIDE_LENGTH)),
                               TransformState.makePos(Vec3(0,0,0.5 * BOX_SIDE_LENGTH)))
    box_rigid_body.node().setMass(1)
    box_rigid_body.node().setLinearFactor((1,0,1))
    box_rigid_body.node().setAngularFactor((0,0,0))
    box_rigid_body.setPos(Vec3(1,0,1))
    box_rigid_body.setCollideMask(BitMask32.allOff())    
    #visual.instanceTo(box_rigid_body)
    
    # create h_shaped rigid body
    h_shaped_body = self.world_node_.attachNewNode(self.createHShapedRigidBody("HBody", BOX_SIDE_LENGTH))
    
    # create hinge
    hinge = self.hingeRigidBodies(box_rigid_body.node(), h_shaped_body.node(),
                                   Vec3(0.5*BOX_SIDE_LENGTH,0,BOX_SIDE_LENGTH), 
                                   Vec3(0,0,BOX_SIDE_LENGTH))

    self.physics_world_.attach(box_rigid_body.node())
    self.physics_world_.attach(h_shaped_body.node())
    self.physics_world_.attach(hinge)
    self.object_nodes_.append(box_rigid_body)
    
  def createHShapedRigidBody(self,name,side_length):
    
    half_side_length = 0.5 * side_length/4
    box_size = Vec3(half_side_length,half_side_length,half_side_length)
    rigid_body = BulletRigidBodyNode(name)
    
    # right side
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(3*half_side_length,0,half_side_length))) # bottom 
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(3*half_side_length,0,3*half_side_length))) # center 1
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(3*half_side_length,0,5*half_side_length))) # center 2
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(3*half_side_length,0,7*half_side_length))) # top 
    
    # left side
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(-3*half_side_length,0,half_side_length))) # bottom 
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(-3*half_side_length,0,3*half_side_length))) # center 1
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(-3*half_side_length,0,5*half_side_length))) # center 2
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(-3*half_side_length,0,7*half_side_length))) # top 
    
    # middle
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(-half_side_length,0,4*half_side_length))) #  left
    rigid_body.addShape(BulletBoxShape(box_size),TransformState.makePos(Vec3(half_side_length,0,4*half_side_length))) #  right
    
    rigid_body.setMass(1)
    rigid_body.setLinearFactor((1,0,1))
    rigid_body.setAngularFactor((0,0,0))
    rigid_body.setIntoCollideMask(BitMask32.allOn())
    
    return rigid_body
  
  def hingeRigidBodies(self,bodyA,bodyB,pointA,pointB):
    
    bodyB.setTransform(bodyA.getTransform())    
    hinge = BulletHingeConstraint(bodyA,bodyB,pointA,Vec3(0,0,1),pointB,Vec3(0,0,1))
    return hinge
    
    
    
    
    
    

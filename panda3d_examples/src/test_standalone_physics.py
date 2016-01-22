#!/usr/bin/env python
import sys
import time

from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import ClockObject

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

LOOP_DELAY = 0.05 # seconds

class TestApplication:

  def __init__(self):

    self.setupPhysics()
    self.clock_ = ClockObject()


  def sim(self):
    
    while True:
        try:
          
          time.sleep(LOOP_DELAY)
          
          self.clock_.tick()
          self.physics_world_.doPhysics(self.clock_.getDt(), 5, 1.0/180.0)

          # printing location of first box
          print "Box 0: %s"%(str(self.boxes_[0].getPos()))

        except KeyboardInterrupt:
            print "Simulation finished"
            sys.exit()

  def setupPhysics(self):

    # setting up physics world and parent node path 
    self.physics_world_ = BulletWorld()
    self.world_node_ = NodePath()
    self.physics_world_.setGravity(Vec3(0, 0, -9.81))

    # setting up ground
    self.ground_ = self.world_node_.attachNewNode(BulletRigidBodyNode('Ground'))
    self.ground_.node().addShape(BulletPlaneShape(Vec3(0, 0, 1), 0))
    self.ground_.setPos(0,0,0)
    self.ground_.setCollideMask(BitMask32.allOn())
    self.physics_world_.attachRigidBody(self.ground_.node())

    self.boxes_ = []
    num_boxes = 20
    side_length = 0.2
    size = Vec3(side_length,side_length,side_length)
    start_pos = Vec3(-num_boxes*side_length,0,10)
    for i in range(0,20):
      self.addBox("name %i"%(i),size,start_pos + Vec3(i*2*side_length,0,0))

  def addBox(self,name,size,pos):

    # Box (dynamic)
    box = self.world_node_.attachNewNode(BulletRigidBodyNode(name))
    box.node().setMass(1.0)
    box.node().addShape(BulletBoxShape(size))
    box.setPos(pos)
    box.setCollideMask(BitMask32.allOn())

    self.physics_world_.attachRigidBody(box.node())
    self.boxes_.append(box)

    

if __name__ == "__main__":

  application = TestApplication()
  application.sim()
 

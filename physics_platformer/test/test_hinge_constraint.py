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

BOX_SIDE_LENGTH = 0.8
HINGE_ANGLE_RIGHT = 0
HINGE_ANGLE_LEFT = 180
RESOURCES_DIR = rospkg.RosPack().get_path('physics_platformer') + '/resources' 

class TestHingeConstraint(TestApplication):
  
  def __init__(self):
    
    self.hinge_ = None
    TestApplication.__init__(self)
    
  def setupControls(self):
    TestApplication.setupControls(self)
    
    self.accept('t',self.toggleLeftRight)
    self.accept('i',lambda: sys.stdout.write(str(taskMgr)))
    self.instructions_.append(self.addInstructions(0.36, "t: Toggle Left Right"))
    self.instructions_.append(self.addInstructions(0.42, "b: Print TaskManager Info"))
    
  def setupPhysics(self):
    
    TestApplication.setupPhysics(self)
    
    # resources
    visual = loader.loadModel(RESOURCES_DIR + '/models/box.egg')
    visual.setTexture(loader.loadTexture(RESOURCES_DIR + '/models/limba.jpg'))
    bounds = visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    logging.debug("Box visual scale factor %f"%(scale_factor))
    
    # create box rigid body
    box_rigid_body = self.world_node_.attachNewNode(BulletRigidBodyNode("Box"))
    box_rigid_body.node().addShape(BulletBoxShape(Vec3(0.5 * BOX_SIDE_LENGTH,0.5 * BOX_SIDE_LENGTH,0.5 * BOX_SIDE_LENGTH)),
                               TransformState.makePos(Vec3(0,0,0.5 * BOX_SIDE_LENGTH)))
    box_rigid_body.node().setMass(1)
    box_rigid_body.node().setLinearFactor((1,0,1))
    box_rigid_body.node().setAngularFactor((0,0,0))
    box_rigid_body.setCollideMask(BitMask32.allOff())    
    vnp = visual.instanceTo(box_rigid_body)   
    vnp.setPos(Vec3(0,0,0.5*BOX_SIDE_LENGTH)) 
    vnp.setScale(BOX_SIDE_LENGTH*scale_factor,BOX_SIDE_LENGTH*scale_factor,BOX_SIDE_LENGTH*scale_factor)    
    box_rigid_body.setPos(Vec3(1,0,2))
    
    # create h_shaped rigid body
    h_shaped_body = self.createHShapedRigidBody("HBody", 1.5*BOX_SIDE_LENGTH)
    h_shaped_body.reparentTo(self.world_node_)
    
    # create hinge
    hinge = self.hingeRigidBodies(box_rigid_body.node(), h_shaped_body.node(),
                                   Vec3(0.5*BOX_SIDE_LENGTH,0,BOX_SIDE_LENGTH), 
                                   Vec3(0,0,BOX_SIDE_LENGTH))
    self.hinge_ = hinge

    self.physics_world_.attach(box_rigid_body.node())
    self.physics_world_.attach(h_shaped_body.node())
    self.physics_world_.attach(hinge)
    self.object_nodes_.append(box_rigid_body)
    self.object_nodes_.append(h_shaped_body)
    
  def cleanup(self):
      
    self.physics_world_.remove(self.hinge_)
    self.hinge_ = None
    TestApplication.cleanup(self) 
    
  def createHShapedRigidBody(self,name,side_length):
    
    visual = loader.loadModel(RESOURCES_DIR + '/models/box.egg')
    visual.setTexture(loader.loadTexture(RESOURCES_DIR + '/models/limba.jpg'))
    bounds = visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    #visual.setScale(side_length*scale_factor,side_length*scale_factor,side_length*scale_factor)
    
    half_side_length = 0.5 * side_length/4
    box_size = Vec3(half_side_length,half_side_length,half_side_length)
    rigid_body = NodePath(BulletRigidBodyNode(name))
    
    transforms = [
                  TransformState.makePos(Vec3(3*half_side_length,0,half_side_length)),    # bottom 
                  TransformState.makePos(Vec3(3*half_side_length,0,3*half_side_length)),  # center 1
                  TransformState.makePos(Vec3(3*half_side_length,0,5*half_side_length)) , # center 2
                  TransformState.makePos(Vec3(3*half_side_length,0,7*half_side_length)) , # top
                  TransformState.makePos(Vec3(-3*half_side_length,0,half_side_length)) ,  # bottom
                  TransformState.makePos(Vec3(-3*half_side_length,0,3*half_side_length)), # center 1
                  TransformState.makePos(Vec3(-3*half_side_length,0,5*half_side_length)), # center 2
                  TransformState.makePos(Vec3(-3*half_side_length,0,7*half_side_length)), # top 
                  TransformState.makePos(Vec3(-half_side_length,0,4*half_side_length)),   # left
                  TransformState.makePos(Vec3(half_side_length,0,4*half_side_length))     # right
                  ]
    
    count = 0
    for t in transforms:
      rigid_body.node().addShape(BulletBoxShape(box_size),t)
      vnp = visual.instanceUnderNode(rigid_body,'box-visual' + str(count))
      vnp.setTransform(t)      
      vnp.setScale(2*half_side_length*scale_factor,
                   2*half_side_length*scale_factor,
                   2*half_side_length*scale_factor)
      vnp.setTexture(loader.loadTexture(RESOURCES_DIR + '/models/limba.jpg'))
      count+=1
      
    rigid_body.node().setMass(1)
    rigid_body.node().setLinearFactor((1,0,1))
    rigid_body.node().setAngularFactor((0,0,0))
    rigid_body.node().setIntoCollideMask(BitMask32.allOn())
    
    return rigid_body
  
  def hingeRigidBodies(self,bodyA,bodyB,pointA,pointB):
    
    bodyB.setTransform(bodyA.getTransform())    
    hinge = BulletHingeConstraint(bodyA,bodyB,pointA,pointB,Vec3(0,0,1),Vec3(0,0,1))
    hinge.setLimit(HINGE_ANGLE_RIGHT,HINGE_ANGLE_RIGHT)
    return hinge
  
  
  # callbacks
  def toggleLeftRight(self):  
      
#     body_btransform = self.hinge_.getFrameB()
#     #body_btransform = TransformState.makeHpr(Vec3(0,0,180))*body_btransform
#     body_btransform = TransformState.makeMat(TransformState.makeHpr(Vec3(0,0,180)).getMat()*body_btransform.getMat())
#     self.hinge_.setFrames(self.hinge_.getFrameA(),body_btransform)
    if abs(self.hinge_.getHingeAngle() - HINGE_ANGLE_RIGHT) < 0.01: 
      self.hinge_.setLimit(HINGE_ANGLE_LEFT,HINGE_ANGLE_LEFT)  
      self.hinge_.enableAngularMotor(True,1000,2)   
      self.hinge_.setMotorTarget(HINGE_ANGLE_LEFT,0.01)
      
    else:      
      self.hinge_.setLimit(HINGE_ANGLE_RIGHT,HINGE_ANGLE_RIGHT)
      self.hinge_.enableAngularMotor(True,-1000,2) 
      self.hinge_.setMotorTarget(HINGE_ANGLE_RIGHT,0.01)
      
    #self.hinge_.enableMotor(False)
      
    logging.info("Hinge angle set to %f"%(self.hinge_.getHingeAngle()))
    logging.info("Hinge limits are [%f , %f]"%(self.hinge_.getLowerLimit(),self.hinge_.getUpperLimit()))
    
    

if __name__ == '__main__':
    
    
    log_level = logging.DEBUG
    try:
        opts, args = getopt.getopt(sys.argv[1:],'l:','log=')
    except getopt.GetoptError:
        logging.error("Invalid use of the %s script"%(sys.argv[0]))
        sys.exit()
        
    for opt,arg in opts:
        if opt in ('-l','--log'):
            
            # Configuring logging level
            log_level = getattr(logging, arg.upper(), None)
            if isinstance(log_level, int):                                
                print "Configuring log level to %s"%(arg.upper())
        
    
    logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)    
    application = TestHingeConstraint()
    application.run()    
    
    
    

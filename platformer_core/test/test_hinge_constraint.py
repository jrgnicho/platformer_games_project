#!/usr/bin/env python3
from direct.interval.Interval import Interval
from platformer_core.test import TestApplication
from platformer_core.game_object import *
from platformer_core.sprite import *
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
from panda3d.bullet import BulletGenericConstraint
from panda3d.bullet import BulletHingeConstraint
from panda3d.bullet import BulletBoxShape
from panda3d.core import TransformState

BOX_SIDE_LENGTH = 0.8
HINGE_ANGLE_RIGHT = 0
HINGE_ANGLE_LEFT = 180
RESOURCES_DIR = rospkg.RosPack().get_path('platformer_core') + '/resources' 

class TestHingeConstraint(TestApplication):
  
  def __init__(self):
    
    self.active_constraint_ = None
    self.left_constraint_ = None
    self.right_constraint_ = None
    self.parent_rigid_body_ = None
    self.child_rigid_body_ = None
    TestApplication.__init__(self)
    
  def setupControls(self):
    TestApplication.setupControls(self)
    
    self.accept('t',self.toggleLeftRight)
    self.accept('i',lambda: sys.stdout.write(str(taskMgr)))
    self.input_state_.watchWithModifiers("move right","j")
    self.input_state_.watchWithModifiers("move left", 'g')
    self.input_state_.watchWithModifiers('move up', 'y')
    self.input_state_.watchWithModifiers('move halt', 'h')
    pos = 0.36
    incr = 0.06
    self.instructions_.append(self.addInstructions(pos, "t: Toggle Left Right")); pos+=incr
    self.instructions_.append(self.addInstructions(pos, "b: Print TaskManager Info")); pos+=incr
    
    self.instructions_.append(self.addInstructions(pos, "j: Move Right")); pos+=incr
    self.instructions_.append(self.addInstructions(pos, "g: Move Left")); pos+=incr
    self.instructions_.append(self.addInstructions(pos, "y: Move Up")); pos+=incr
    self.instructions_.append(self.addInstructions(pos, "h: Move Halt")); pos+=incr
    
  def processInput(self,dt):
    TestApplication.processInput(self,dt)
    
    apply_vel = False
    vel = self.parent_rigid_body_.node().getLinearVelocity()
    if self.input_state_.isSet('move right'): 
      vel.setX(2)
      apply_vel = True

    if self.input_state_.isSet('move left'): 
      vel.setX(-2)
      apply_vel = True

    if self.input_state_.isSet('move up'): 
      vel.setZ(4)
      apply_vel = True

    if self.input_state_.isSet('move halt'): 
      vel.setX(0)
      apply_vel = True
    
    if apply_vel:
      self.parent_rigid_body_.node().setActive(True,True)
      self.parent_rigid_body_.node().setLinearVelocity(vel)
    
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
    #box_rigid_body = NodePath(BulletRigidBodyNode("Box"))
    box_rigid_body.node().addShape(BulletBoxShape(Vec3(0.5 * BOX_SIDE_LENGTH,0.5 * BOX_SIDE_LENGTH,0.5 * BOX_SIDE_LENGTH)),
                               TransformState.makePos(Vec3(0,0,0.5 * BOX_SIDE_LENGTH)))
    box_rigid_body.node().setMass(1)
    box_rigid_body.node().setLinearFactor((1,0,1))
    box_rigid_body.node().setAngularFactor((0,0,0))
    box_rigid_body.setCollideMask(BitMask32.allOff())    
    vnp = visual.instanceTo(box_rigid_body)   
    vnp.setPos(Vec3(0,0,0.5*BOX_SIDE_LENGTH)) 
    vnp.setScale(BOX_SIDE_LENGTH*scale_factor,BOX_SIDE_LENGTH*scale_factor,BOX_SIDE_LENGTH*scale_factor)    
    box_rigid_body.setPos(Vec3(1.5,0,2))
    
    # create h_shaped rigid body
    h_shaped_body = self.createHShapedRigidBody("HBody", 1.5*BOX_SIDE_LENGTH)
    h_shaped_body.reparentTo(self.world_node_)
    h_shaped_body.setPos(box_rigid_body,Vec3(0,0,0))
    h_shaped_body.setH(box_rigid_body,180)
    
    # create constraints
    self.right_constraint_, self.left_constraint_ = self.createConstraints(box_rigid_body.node(),h_shaped_body.node())
    self.active_constraint_ = self.left_constraint_
    self.active_constraint_.setEnabled(True)
    self.parent_rigid_body_ = box_rigid_body
    self.child_rigid_body_ = h_shaped_body

    self.physics_world_.attach(box_rigid_body.node())
    self.physics_world_.attach(h_shaped_body.node())
    self.physics_world_.attach(self.active_constraint_)
    self.object_nodes_.append(box_rigid_body)
    self.object_nodes_.append(h_shaped_body)
    
    
  def cleanup(self):
      
    self.physics_world_.remove(self.active_constraint_)
    self.right_constraint_ = None
    self.left_constraint_ = None
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
                  TransformState.makePos(Vec3(0.5*side_length + 3*half_side_length,0,half_side_length)),    # bottom 
                  TransformState.makePos(Vec3(0.5*side_length + 3*half_side_length,0,3*half_side_length)),  # center 1
                  TransformState.makePos(Vec3(0.5*side_length + 3*half_side_length,0,5*half_side_length)) , # center 2
                  TransformState.makePos(Vec3(0.5*side_length + 3*half_side_length,0,7*half_side_length)) , # top
                  TransformState.makePos(Vec3(0.5*side_length + -3*half_side_length,0,half_side_length)) ,  # bottom
                  TransformState.makePos(Vec3(0.5*side_length + -3*half_side_length,0,3*half_side_length)), # center 1
                  TransformState.makePos(Vec3(0.5*side_length + -3*half_side_length,0,5*half_side_length)), # center 2
                  TransformState.makePos(Vec3(0.5*side_length + -3*half_side_length,0,7*half_side_length)), # top 
                  TransformState.makePos(Vec3(0.5*side_length + -half_side_length,0,4*half_side_length)),   # left
                  TransformState.makePos(Vec3(0.5*side_length + half_side_length,0,4*half_side_length))     # right
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
  
  
  def createConstraints(self,bodyA,bodyB):
    
    left_constraint = BulletGenericConstraint(bodyA,bodyB,TransformState.makeIdentity(),TransformState.makeHpr(Vec3(180,0,0)),False)
    right_constraint = BulletGenericConstraint(bodyA,bodyB,TransformState.makeIdentity(),TransformState.makeIdentity(),False)
    left_constraint.setEnabled(False)
    right_constraint.setEnabled(False)
    return (right_constraint,left_constraint)
  
  
  # callbacks
  def toggleLeftRight(self):  
      
    self.active_constraint_.setEnabled(False)
    self.physics_world_.remove(self.active_constraint_)
    self.child_rigid_body_.node().setStatic(True)
    if self.active_constraint_ == self.right_constraint_:
      self.active_constraint_ = self.left_constraint_
      self.child_rigid_body_.setH(self.parent_rigid_body_,180)
      logging.info("Left Constraint is active")
    else:
      self.active_constraint_ = self.right_constraint_
      self.child_rigid_body_.setH(self.parent_rigid_body_,0)
      logging.info("Right Constraint is active")
    
    self.child_rigid_body_.node().setStatic(False) 
    self.active_constraint_.setEnabled(True)  
    self.physics_world_.attach(self.active_constraint_)
      
    
    

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
                print("Configuring log level to %s"%(arg.upper()))
        
    
    logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)    
    application = TestHingeConstraint()
    application.run()    
    
    
    

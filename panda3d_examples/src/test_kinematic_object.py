#!/usr/bin/env python
import sys
import time

from direct.showbase.ShowBase import ShowBase
from direct.controls.InputState import InputState
from direct.gui.OnscreenText import OnscreenText

from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import ClockObject
from panda3d.core import TextNode

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

LOOP_DELAY = 0.05 # seconds
CAM_DISTANCE =  20
ROTATIONAl_SPEED = 20

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), scale=.08,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))

class TestApplication(ShowBase):

  def __init__(self):

    ShowBase.__init__(self)

    self.setupRendering()
    self.setupControls()
    self.setupPhysics()
    #self.cam.reparentTo(self.world_node_)
    self.clock_ = ClockObject()
    self.controlled_obj_index_ = 0
    self.kinematic_mode_ = False
  
    # Task
    taskMgr.add(self.update, 'updateWorld')


  def setupRendering(self):

    self.setBackgroundColor(0.1, 0.1, 0.8, 1)
    self.setFrameRateMeter(True)

    # Light
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
    alightNP = self.render.attachNewNode(alight)

    dlight = DirectionalLight('directionalLight')
    dlight.setDirection(Vec3(1, 1, -1))
    dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    dlightNP = self.render.attachNewNode(dlight)

    self.render.clearLight()
    self.render.setLight(alightNP)
    self.render.setLight(dlightNP)

  def setupControls(self):

    # Input (Events)
    self.accept('escape', self.doExit)
    self.accept('r', self.doReset)
    self.accept('f1', self.toggleWireframe)
    self.accept('f2', self.toggleTexture)
    self.accept('f3', self.toggleDebug)
    self.accept('f5', self.doScreenshot)
    self.accept('n', self.selectNextControlledObject)
    self.accept('k', self.toggleKinematicMode)

    # Inputs (Polling)
    self.input_state_ = InputState()
    self.input_state_.watchWithModifiers("right","arrow_right")
    self.input_state_.watchWithModifiers('left', 'arrow_left')
    self.input_state_.watchWithModifiers('jump', 'arrow_up')
    self.input_state_.watchWithModifiers('stop', 'arrow_down')
    self.input_state_.watchWithModifiers('roll_right', 'c')
    self.input_state_.watchWithModifiers('roll_left', 'z')
    self.input_state_.watchWithModifiers('roll_stop', 'x')


    self.title = addTitle("Panda3D: Kinematic Objects")
    self.inst1 = addInstructions(0.06, "ESC: Quit")
    self.inst2 = addInstructions(0.12, "Up/Down: Jump/Stop")
    self.inst3 = addInstructions(0.18, "Left/Right: Move Left / Move Rigth")
    self.inst4 = addInstructions(0.24, "z/x/c : Rotate Left/ Rotate Stop / Rotate Right")
    self.inst5 = addInstructions(0.30, "n: Select Next Character")
    self.inst6 = addInstructions(0.36, "k: Toggle Kinematic Mode")
    self.inst7 = addInstructions(0.42, "f1: Toggle Wireframe")
    self.inst8 = addInstructions(0.48, "f2: Toggle Texture")
    self.inst9 = addInstructions(0.54, "f3: Toggle BulletDebug")
    self.inst10 = addInstructions(0.60, "f5: Capture Screenshot")



  def setupPhysics(self):

    # setting up physics world and parent node path 
    self.physics_world_ = BulletWorld()
    self.world_node_ = self.render.attachNewNode('world')
    self.cam.reparentTo(self.world_node_)
    self.physics_world_.setGravity(Vec3(0, 0, -9.81))

    self.debug_node_ = self.world_node_.attachNewNode(BulletDebugNode('Debug'))
    self.debug_node_.node().showWireframe(True)
    self.debug_node_.node().showConstraints(True)
    self.debug_node_.node().showBoundingBoxes(True)
    self.debug_node_.node().showNormals(True)
    self.physics_world_.setDebugNode(self.debug_node_.node())
    self.debug_node_.hide()

    # setting up ground
    self.ground_ = self.world_node_.attachNewNode(BulletRigidBodyNode('Ground'))
    self.ground_.node().addShape(BulletPlaneShape(Vec3(0, 0, 1), 0))
    self.ground_.setPos(0,0,0)
    self.ground_.setCollideMask(BitMask32.allOn())
    self.physics_world_.attachRigidBody(self.ground_.node())

    self.object_nodes_ = []
    self.controlled_objects_=[]
    num_boxes = 20
    side_length = 0.2
    size = Vec3(0.5*side_length,0.5*side_length,0.5*side_length)
    start_pos = Vec3(-num_boxes*side_length,0,6)

    # creating boxes
    box_visual = loader.loadModel('models/box.egg')
    box_visual.clearModelNodes()
    box_visual.setTexture(loader.loadTexture('models/wood.png'))
    #box_visual.setRenderModeWireframe()
    bounds = box_visual.getTightBounds() # start of box model scaling
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = side_length/max([extents.getX(),extents.getY(),extents.getZ()])
    box_visual.setScale((scale_factor,scale_factor ,scale_factor)) # end of box model scaling

    for i in range(0,20):
      self.addBox("name %i"%(i),size,start_pos + Vec3(i*side_length,0,0),box_visual)

    start_pos = Vec3(-num_boxes*side_length,0,8)
    for i in range(0,20):
      self.addBox("name %i"%(i),size,start_pos + Vec3(i*2*side_length,0,0),box_visual)


    # creating sphere
    diameter = 0.4
    sphere_visual = loader.loadModel('models/ball.egg')

    bounds = sphere_visual.getTightBounds() # start of model scaling
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = diameter/max([extents.getX(),extents.getY(),extents.getZ()])
    sphere_visual.clearModelNodes()
    sphere_visual.setScale(scale_factor,scale_factor,scale_factor) # end of model scaling

    sphere_visual.setTexture(loader.loadTexture('models/bowl.jpg'))
    sphere = self.world_node_.attachNewNode(BulletRigidBodyNode('Sphere'))
    sphere.node().addShape(BulletSphereShape(0.5*diameter))
    sphere.node().setMass(1.0)
    sphere.node().setLinearFactor((1,0,1))
    sphere.node().setAngularFactor((0,1,0))
    sphere.setCollideMask(BitMask32.allOn())
    sphere_visual.instanceTo(sphere)
    sphere.setPos(Vec3(0,0,size.getZ()+1))
    
    self.physics_world_.attachRigidBody(sphere.node())
    self.object_nodes_.append(sphere)
    self.controlled_objects_.append(sphere)

    # creating mobile box
    size = Vec3(0.2,0.2,0.4)
    mbox_visual = loader.loadModel('models/box.egg')
    bounds = mbox_visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    mbox_visual.setScale(size.getX()*scale_factor,size.getY()*scale_factor,size.getZ()*scale_factor)

    mbox = self.world_node_.attachNewNode(BulletRigidBodyNode('MobileBox'))
    mbox.node().addShape(BulletBoxShape(size/2))
    mbox.node().setMass(1.0)
    mbox.node().setLinearFactor((1,0,1))
    mbox.node().setAngularFactor((0,1,0))
    mbox.setCollideMask(BitMask32.allOn())
    mbox_visual.instanceTo(mbox)
    mbox.setPos(Vec3(1,0,size.getZ()+1))
    
    self.physics_world_.attachRigidBody(mbox.node())
    self.object_nodes_.append(mbox)
    self.controlled_objects_.append(mbox)

    self.setupLevel()


  def addBox(self,name,size,pos,visual):

    # Box (dynamic)
    box = self.world_node_.attachNewNode(BulletRigidBodyNode(name))
    box.node().setMass(1.0)
    box.node().addShape(BulletBoxShape(size))
    box.setPos(pos)
    box.setCollideMask(BitMask32.allOn())
    box.node().setLinearFactor((1,0,1))
    box.node().setAngularFactor((0,1,0))
    visual.instanceTo(box)

    self.physics_world_.attachRigidBody(box.node())
    self.object_nodes_.append(box)

  def setupLevel(self):

    # (left, top, length ,depth(y) ,height)
    platform_details =[ 
      (-20, 4, 20, 4, 1  ),
      (-2, 5, 10, 4, 1  ),
      ( 4 , 2 , 16, 4, 1.4),
      (-4 , 1, 10, 4, 1),
      ( 16, 6, 30, 4, 1)
      ]

    # Platform Visuals
    visual = loader.loadModel('models/box.egg')
    visual.setTexture(loader.loadTexture('models/iron.jpg'))
    
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      topleft = (p[0],p[1])
      size = Vec3(p[2],p[3],p[4])
      self.addPlatform(topleft, size,'Platform%i'%(i),visual)


  def addPlatform(self,topleft,size,name,visual):


    # Box (static)
    platform = self.world_node_.attachNewNode(BulletRigidBodyNode(name))
    platform.node().setMass(0)
    platform.node().addShape(BulletBoxShape(size/2))
    platform.setPos(Vec3(topleft[0] + 0.5*size.getX(),0,topleft[1]-0.5*size.getZ()))
    platform.setCollideMask(BitMask32.allOn())
    local_visual = visual.instanceUnderNode(platform,name + '_visual')

    # Visual scaling
    bounds = local_visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    local_visual.setScale(size.getX()*scale_factor,size.getY()*scale_factor,size.getZ()*scale_factor)
    

    self.physics_world_.attachRigidBody(platform.node())
    self.object_nodes_.append(platform)

  def update(self, task):

    self.clock_.tick()
    dt = self.clock_.getDt()
    self.processInput(dt)    
    self.physics_world_.doPhysics(dt, 5, 1.0/180.0)
    self.updateCamera()

    return task.cont 

  def processInput(self,dt):
  
    activate = False
    obj = self.controlled_objects_[self.controlled_obj_index_]

    if self.kinematic_mode_:
      obj.node().setKinematic(True)
      return
    else:
      obj.node().setKinematic(False)

    vel = obj.node().getLinearVelocity()
    w = obj.node().getAngularVelocity()

  
    if self.input_state_.isSet('right'): 
      vel.setX(2)
      activate = True

    if self.input_state_.isSet('left'): 
      vel.setX(-2)
      activate = True

    if self.input_state_.isSet('jump'): 
      vel.setZ(4)
      activate = True

    if self.input_state_.isSet('stop'): 
      vel.setX(0)

    if self.input_state_.isSet('roll_right'):
      w.setY(ROTATIONAl_SPEED)
      activate = True

    if self.input_state_.isSet('roll_left'):
      w.setY(-ROTATIONAl_SPEED)
      activate = True

    if self.input_state_.isSet('roll_stop'):
      w.setY(0)

    if activate : obj.node().setActive(True,True)
    obj.node().setLinearVelocity(vel)
    obj.node().setAngularVelocity(w)

  def updateCamera(self):

    if len(self.controlled_objects_) > 0:
      obj = self.controlled_objects_[self.controlled_obj_index_]
      self.cam.setPos(obj,0, -CAM_DISTANCE, 0)
      self.cam.lookAt(obj.getPos())

  def cleanup(self):
    
    for i in range(0,len(self.object_nodes_)):
      rb = self.object_nodes_[i]
      self.physics_world_.removeRigidBody(rb.node())

    self.object_nodes_ = []
    self.controlled_objects_ = []
    self.physics_world_.removeRigidBody(self.ground_.node())
    self.ground_ = None
    self.physics_world_ = None
    self.debug_node_ = None
    self.cam.reparentTo(self.render)
    self.world_node_.removeNode()
    self.world_node_ = None

  # _____HANDLER_____

  def toggleKinematicMode(self):
    self.kinematic_mode_ = not self.kinematic_mode_

    print "Kinematic Mode %s"%('ON' if self.kinematic_mode_ else 'OFF')

  def selectNextControlledObject(self):
    self.controlled_obj_index_+=1
    if self.controlled_obj_index_ >= len(self.controlled_objects_):
      self.controlled_obj_index_ = 0 #  reset


  def doExit(self):
    self.cleanup()
    sys.exit(1)

  def doReset(self):
    self.cleanup()
    self.setupPhysics()

  def toggleDebug(self):

    if self.debug_node_.isHidden():
      self.debug_node_.show()
    else:
      self.debug_node_.hide()

  def doScreenshot(self):
    self.screenshot('Bullet')

if __name__ == "__main__":

  application = TestApplication()
  application.run()
 

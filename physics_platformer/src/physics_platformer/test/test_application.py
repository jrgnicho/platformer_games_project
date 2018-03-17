import sys
import time
import rospkg

from direct.showbase.ShowBase import ShowBase
from direct.controls.InputState import InputState
from direct.gui.OnscreenText import OnscreenText

from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import LColor
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import ClockObject
from panda3d.core import PNMImage, PNMImageHeader, Filename
from panda3d.core import SequenceNode
from panda3d.core import CardMaker
from panda3d.core import Texture
from panda3d.core import TextureStage
from panda3d.core import TransparencyAttrib
from panda3d.core import TextNode

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

RESOURCES_DIR = rospkg.RosPack().get_path('physics_platformer') + '/resources'  

class TestApplication(ShowBase):

  def __init__(self,name = 'TestApplication', cam_step = 0.05, cam_zoom = 4):

    ShowBase.__init__(self)
    
    self.cam_step_ = cam_step
    self.cam_zoom_ = cam_zoom
    self.name_ = name
    self.setupRendering()
    self.setupResources()
    self.setupControls()
    self.setupPhysics()
    self.clock_ = ClockObject()
  
    # Task
    taskMgr.add(self.update, 'updateWorld')
    
    # Function to put instructions on the screen.    
  def addInstructions(self,pos, msg):
      return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                pos=(0.08, -pos - 0.04), align=TextNode.ALeft)
    
    # Function to put title on the screen.
  def addTitle(self,text):
      return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), scale=.08,
                parent=base.a2dBottomRight, align=TextNode.ARight,
                pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))

  def setupResources(self):
    pass

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
    self.accept('q',self.zoomIn)
    self.accept('a',self.zoomOut)

    # Inputs (Polling)
    self.input_state_ = InputState()
    self.input_state_.watchWithModifiers("right","arrow_right")
    self.input_state_.watchWithModifiers('left', 'arrow_left')
    self.input_state_.watchWithModifiers('up', 'arrow_up')
    self.input_state_.watchWithModifiers('down', 'arrow_down')


    self.title = self.addTitle("Panda3D: " + self.name_)
    self.instructions_ = [
                          self.addInstructions(0.06, "ESC: Quit"),
                          self.addInstructions(0.12, "Up/Down: Jump/Stop"),
                          self.addInstructions(0.18, "Left/Right: Move Left / Move Rigth"),
                          self.addInstructions(0.24, "z/x/c : Rotate Left/ Rotate Stop / Rotate Right"),
                          self.addInstructions(0.30, "q/a: Zoom in / Zoom out")
                          ]
    
    
    
    


  def setupPhysics(self, use_default_objs = True):

    # setting up physics world and parent node path 
    self.physics_world_ = BulletWorld()
    self.world_node_ = self.render.attachNewNode('world')
    self.cam.reparentTo(self.world_node_)
    self.cam.setPos(self.world_node_,0, -self.cam_zoom_*6, self.cam_step_*25)
    self.physics_world_.setGravity(Vec3(0, 0, -9.81))

    self.debug_node_ = self.world_node_.attachNewNode(BulletDebugNode('Debug'))
    self.debug_node_.show()
    self.debug_node_.node().showWireframe(True)
    self.debug_node_.node().showConstraints(True)
    self.debug_node_.node().showBoundingBoxes(False)
    self.debug_node_.node().showNormals(True)    
    self.physics_world_.setDebugNode(self.debug_node_.node())
    self.debug_node_.hide()
    self.object_nodes_ = []
    self.controlled_objects_ = []
    
    self.ground_ = None
    if use_default_objs:

      # setting up ground
      self.ground_ = self.world_node_.attachNewNode(BulletRigidBodyNode('Ground'))
      self.ground_.node().addShape(BulletPlaneShape(Vec3(0, 0, 1), 0))
      self.ground_.setPos(0,0,0)
      self.ground_.setCollideMask(BitMask32.allOn())
      self.physics_world_.attachRigidBody(self.ground_.node())
  
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
      ( 4 , 2 , 16, 4, 1),
      (-4 , 1, 10, 4, 1),
      ( 16, 6, 30, 4, 1)
      ]
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      topleft = (p[0],p[1])
      size = Vec3(p[2],p[3],p[4])
      self.addPlatform(topleft, size,'Platform%i'%(i))


  def addPlatform(self,topleft,size,name):

    # Visual
    visual = loader.loadModel(RESOURCES_DIR + '/models/box.egg')
    visual.clearModelNodes()
    visual.setTexture(loader.loadTexture(RESOURCES_DIR + '/models/iron.jpg'),1)
    bounds = visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    visual.setScale(size.getX()*scale_factor,size.getY()*scale_factor,size.getZ()*scale_factor)
    
    # Box (static)
    platform = self.world_node_.attachNewNode(BulletRigidBodyNode(name))
    platform.node().setMass(0)
    platform.node().addShape(BulletBoxShape(size/2))
    platform.setPos(Vec3(topleft[0] + 0.5*size.getX(),0,topleft[1]-0.5*size.getZ()))
    platform.setCollideMask(BitMask32.allOn())
    visual.instanceTo(platform)

    self.physics_world_.attachRigidBody(platform.node())
    self.object_nodes_.append(platform)

  def update(self, task):

    self.clock_.tick()
    dt = self.clock_.getDt()
    self.processInput(dt)    
    self.physics_world_.doPhysics(dt, 5, 1.0/180.0)
    #self.updateCamera()    

    return task.cont 

  def processInput(self,dt):
      
        
    if self.input_state_.isSet('right'): 
      self.moveRight()

    if self.input_state_.isSet('left'): 
      self.moveLeft()

    if self.input_state_.isSet('up'): 
      self.moveUp()

    if self.input_state_.isSet('down'): 
      self.moveDown()
     

  def updateCamera(self):
      
    #self.cam.setY(-self.cam_zoom_)
    pass

  def cleanup(self):
    
    for i in range(0,len(self.object_nodes_)):
      rb = self.object_nodes_[i]
      self.physics_world_.removeRigidBody(rb.node())

    self.object_nodes_ = []
    
    if self.ground_ is not None:
      self.physics_world_.removeRigidBody(self.ground_.node())
      self.ground_ = None
      
    self.physics_world_ = None
    self.debug_node_ = None
    self.cam.reparentTo(self.render)
    self.world_node_.removeNode()
    self.world_node_ = None
    
  # _____MOVE_METHODS____
  def moveUp(self):
      self.cam.setPos(self.cam.getPos() + Vec3(0, 0,self.cam_step_))
      
  def moveDown(self):
      self.cam.setPos(self.cam.getPos() + Vec3(0, 0,-self.cam_step_))
  
  def moveRight(self):
      self.cam.setPos(self.cam.getPos() + Vec3(self.cam_step_,0,0))
  
  def moveLeft(self):
      self.cam.setPos(self.cam.getPos() + Vec3(-self.cam_step_,0,0))

  # _____HANDLER_____


  def zoomIn(self):
    #global self.cam_zoom_
    self.cam.setY(self.cam.getY()+self.cam_zoom_)

  def zoomOut(self):
    #global self.cam_zoom_
    self.cam.setY(self.cam.getY()-self.cam_zoom_)

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
    self.screenshot('Pand3d')

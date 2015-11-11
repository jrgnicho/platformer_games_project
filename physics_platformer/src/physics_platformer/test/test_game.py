import sys
import time

from direct.showbase.ShowBase import ShowBase
from direct.controls.InputState import InputState
from direct.gui.OnscreenText import OnscreenText

from panda3d.core import loadPrcFileData
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

from physics_platformer.game_level import Level
from physics_platformer.game_level import Platform
from physics_platformer.input import Move
from physics_platformer.input import KeyboardButtons
from physics_platformer.input import KeyboardController
from physics_platformer.game_object import GameObject

class TestGame(ShowBase):
  
  __CAM_ZOOM__ =  1
  __CAM_STEP__ = 0.2
  __NUM_BOXES__ = 0
  __BOX_SIDE_LENGTH__ = 0.4
  
  def __init__(self,name ='TestGame'):
    
    # configure to use group-mask collision filtering mode in the bullet physics world
    loadPrcFileData('', 'bullet-filter-algorithm groups-mask')
    
    ShowBase.__init__(self)   
    
    self.name_ = name
    self.setupRendering()
    self.setupResources()
    self.setupControls()
    self.setupScene()
    self.clock_ = ClockObject()
  
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
    
    self.input_state_ = InputState()
    button_map = {'a' : KeyboardButtons.KEY_A , 'q' : KeyboardButtons.KEY_Q,'escape' : KeyboardButtons.KEY_ESC,
                  'f1' : KeyboardButtons.KEY_F1}
    self.input_manager_ = KeyboardController(self.input_state_, button_map)
    
    # Creating directional moves
    self.input_manager_.add_move(Move('UP',[KeyboardButtons.DPAD_UP],False,lambda : self.moveCamUp()))
    self.input_manager_.add_move(Move('DOWN',[KeyboardButtons.DPAD_DOWN],False,lambda : self.moveCamDown()))
    self.input_manager_.add_move(Move('LEFT',[KeyboardButtons.DPAD_LEFT],False,lambda : self.moveCamLeft()))
    self.input_manager_.add_move(Move('RIGHT',[KeyboardButtons.DPAD_RIGHT],False,lambda : self.moveCamRight()))
    self.input_manager_.add_move(Move('ZoomIn',[KeyboardButtons.KEY_A],False,lambda : self.zoomIn()))
    self.input_manager_.add_move(Move('ZoomOut',[KeyboardButtons.KEY_Q],False,lambda : self.zoomOut()))
    self.input_manager_.add_move(Move('F1',[KeyboardButtons.KEY_F1],False,lambda : self.toggleDebug()))
    self.input_manager_.add_move(Move('EXIT',[KeyboardButtons.KEY_ESC],False,lambda : self.exit()))
    
    
    self.title = self.createTitle("Panda3D: " + self.name_)
    self.instructions_ = [
                          self.createInstruction(0.06, "ESC: Quit"),
                          self.createInstruction(0.12, "Up/Down: Move Camera Up/Down"),
                          self.createInstruction(0.18, "Left/Right: Move Camera Left / Rigth"),
                          self.createInstruction(0.24, "q/a: Zoom in / Zoom out"),
                          self.createInstruction(0.30, "F1: Toggle Debug")
                          ]
  
  def setupScene(self):
    
    self.__setupLevel__()
    self.__setupGameObjects__()
    
    # enable debug visuals
    self.debug_node_ = self.level_.attachNewNode(BulletDebugNode('Debug'))
    self.debug_node_.show()
    self.debug_node_.node().showWireframe(True)
    self.debug_node_.node().showConstraints(True)
    self.debug_node_.node().showBoundingBoxes(False)
    self.debug_node_.node().showNormals(True)    
    self.level_.getPhysicsWorld().setDebugNode(self.debug_node_.node())
    
    self.cam.reparentTo(self.level_)
    self.cam.setPos(self.level_,0, -TestGame.__CAM_ZOOM__*24, TestGame.__CAM_STEP__*25)
    
  def setupResources(self):
    pass  
  
  def cleanup(self):    
    self.level_.detachNode()
    self.level_ = None
    self.input_manager_ = None
  
  def update(self,task):
    self.clock_.tick()
    dt = self.clock_.getDt()
    self.level_.update(dt)
    self.input_manager_.update(dt)
    
    return task.cont
    
  def __setupLevel__(self):

    self.level_ = Level("Level1",Vec3(60,1,60))
    self.level_.reparentTo(self.render)

    # Adding platforms
    platform_details =[ 
      (-20, 4, 20, 4, 1  ),
      (-2, 5, 10, 4, 1  ),
      ( 4 , 2 , 16, 4, 1),
      (-4 , 1, 10, 4, 1),
      ( 16, 6, 30, 4, 1)
      ]
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      pos = Vec3(p[0],0,p[1])
      size = Vec3(p[2],p[3],p[4])
      
      platform = Platform('Platform' + str(i),size)
      self.level_.addPlatform(platform)
      platform.setPos(pos)
      
  def __setupGameObjects__(self):
    
    box_size = Vec3(TestGame.__BOX_SIDE_LENGTH__,TestGame.__BOX_SIDE_LENGTH__,TestGame.__BOX_SIDE_LENGTH__)
    start_pos = Vec3(-TestGame.__NUM_BOXES__*TestGame.__BOX_SIDE_LENGTH__*0.5,0,6)
    for i in range(0,TestGame.__NUM_BOXES__):            
        obj = GameObject("obj"+str(i),box_size,True)
        self.level_.addGameObject(obj)
        obj.setPos(start_pos + Vec3(i*TestGame.__BOX_SIDE_LENGTH__*0.5,0,i*TestGame.__BOX_SIDE_LENGTH__*1.2))    
        
  # __ CAM_METHODS __
  def moveCamUp(self):
      self.cam.setPos(self.cam.getPos() + Vec3(0, 0,TestGame.__CAM_STEP__))
      
  def moveCamDown(self):
      self.cam.setPos(self.cam.getPos() + Vec3(0, 0,-TestGame.__CAM_STEP__))
  
  def moveCamRight(self):
      self.cam.setPos(self.cam.getPos() + Vec3(TestGame.__CAM_STEP__,0,0))
  
  def moveCamLeft(self):
      self.cam.setPos(self.cam.getPos() + Vec3(-TestGame.__CAM_STEP__,0,0))
      
  def zoomIn(self):
    self.cam.setY(self.cam.getY()+TestGame.__CAM_ZOOM__)

  def zoomOut(self):
    self.cam.setY(self.cam.getY()-TestGame.__CAM_ZOOM__)
    
  def toggleDebug(self):
    if self.debug_node_.isHidden():
      self.debug_node_.show()
    else:
      self.debug_node_.hide()
      
  # __ END OF CAM METHODS __
  
  # SUPPORT METHODS
  def createInstruction(self,pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
              shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
              pos=(0.08, -pos - 0.04), align=TextNode.ALeft)
    
    # Function to put title on the screen.
  def createTitle(self,text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), scale=.08,
              parent=base.a2dBottomRight, align=TextNode.ARight,
              pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))
      
  def exit(self):
    self.cleanup()
    sys.exit(1)
      
    
    
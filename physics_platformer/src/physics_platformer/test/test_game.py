import sys
import time

from rospkg import rospack

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

from physics_platformer.state_machine import StateMachine
from physics_platformer.game_level import Level
from physics_platformer.game_level import Platform
from physics_platformer.input import Move
from physics_platformer.input import KeyboardButtons
from physics_platformer.input import KeyboardController
from physics_platformer.game_object import GameObject
from physics_platformer.camera import CameraController

class TestLevel(Level):
  
  def __init__(self,name,min_point,max_point):
    Level.__init__(self,name,min_point, max_point)
    self.setup()
    
  def setup(self):
    
    num_sectors = 6
    sector_lenght = 100
    
    
    
  def __createPlatforms__(self,sector):
    # Adding platforms
    platform_details =[ 
      (-20, 4, 20, TestGame.__PLATFORM_DEPTH__, 1  ),
      (-2, 5, 10, TestGame.__PLATFORM_DEPTH__, 1  ),
      ( 4 , 1 , 16, TestGame.__PLATFORM_DEPTH__, 2),
      (-4 , 1, 10, TestGame.__PLATFORM_DEPTH__, 1),
      ( 16, 6, 30, TestGame.__PLATFORM_DEPTH__, 1),
      ( 0, -0.5, 30, TestGame.__PLATFORM_DEPTH__, 1),
      ]
    
    # Platforms Schematic X, Z (Each new line measures 2 units and each character 2 units)
    
    '''                               
      30                                   _______
                                          |___18__|        ______
                                          | |  ___________|      |
                                          | | |_____26____|      |
                            _________     | |___          |  16  |
      20   ________        |         |    | |10_|   ______|______|
          |___20___|       |____22___|    |6|__    |__18___|
                 __________|_14__|        | |8_|   _____
                |_____28_____|     _______|_|___  |_14__|     __
                                  |_____32______|            |8_|
      10    ||           ___________    ____________       
            ||          |_____26____|  |            |
            |6|                        |_____28_____|
                                                                                    
                                                                                           
      0                                                                                      
          0   10   20   30   40   50   60   70   80   90   100
    '''
    
    # Platform Details [ (float left, float top, Vec3 size),... ]
    platform_details = []
    
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      pos = Vec3(p[0],TestGame.__PLATFORM_Y_POS,p[1])
      size = Vec3(p[2],p[3],p[4])
      
      platform = Platform('Platform' + str(i),size)
      self.level_.addPlatform(platform)
      platform.setPos(sector,pos)

class TestGame(ShowBase):
  
  __CAM_ZOOM__ =  1
  __CAM_STEP__ = 0.2
  __CAM_ORIENT_STEP__ = 4.0
  __NUM_BOXES__ = 10
  __BOX_SIDE_LENGTH__ = 0.4
  
  __BACKGROUND_IMAGE_PACKAGE__ = 'physics_platformer'
  __BACKGROUND_IMAGE_PATH__ = rospack.RosPack().get_path(__BACKGROUND_IMAGE_PACKAGE__) + '/resources/backgrounds/' + 'sky02.png'
  __BACKGROUND_POSITION__ = Vec3(0,100,0)
  __BACKGROUND_SCALE__ = 0.2
  
  __PLATFORM_DEPTH__ = 10
  __PLATFORM_Y_POS = 4
  
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
    
    self.setupBackgroundImage()
    
  def setupBackgroundImage(self):    
    
    image_file = Filename(TestGame.__BACKGROUND_IMAGE_PATH__)
    
    # check if image can be loaded
    img_head = PNMImageHeader()
    if not img_head.readHeader(image_file ):
        raise IOError, "PNMImageHeader could not read file %s. Try using absolute filepaths"%(image_file.c_str())
        sys.exit()
        
    # Load the image with a PNMImage
    w = img_head.getXSize()
    h = img_head.getYSize()
    img = PNMImage(w,h)
    #img.alphaFill(0)
    img.read(image_file) 
    
    texture = Texture()        
    texture.setXSize(w)
    texture.setYSize(h)
    texture.setZSize(1)    
    texture.load(img)
    texture.setWrapU(Texture.WM_border_color) # gets rid of odd black edges around image
    texture.setWrapV(Texture.WM_border_color)
    texture.setBorderColor(LColor(0,0,0,0))
    
    # creating CardMaker to hold the texture
    cm = CardMaker('background')
    cm.setFrame(-0.5*w,0.5*w,-0.5*h,0.5*h)  # This configuration places the image's topleft corner at the origin (left, right, bottom, top)
    background_np = NodePath(cm.generate())            
    background_np.setTexture(texture)
    
    background_np.reparentTo(self.render)
    background_np.setPos(TestGame.__BACKGROUND_POSITION__)
    background_np.setScale(TestGame.__BACKGROUND_SCALE__)
    
  def setupControls(self):
    
       # Input (Events)
    self.accept('escape', self.exit)
    self.accept('r', self.doReset)
    self.accept('f1', self.toggleDebug)
    self.accept('f2', self.toggleTexture)
    self.accept('f3', self.toggleWireframe)
    self.accept('f5', self.doScreenshot)
    
    self.input_state_ = InputState()
    button_map = {'a' : KeyboardButtons.KEY_A , 'q' : KeyboardButtons.KEY_Q,'escape' : KeyboardButtons.KEY_ESC,
                  'f1' : KeyboardButtons.KEY_F1,
                  'e': KeyboardButtons.KEY_E,'w': KeyboardButtons.KEY_W}
    self.input_manager_ = KeyboardController(self.input_state_, button_map)
    
    # Creating directional moves
    self.input_manager_.addMove(Move('UP',[KeyboardButtons.DPAD_UP],False,lambda : self.moveCamUp()))
    self.input_manager_.addMove(Move('DOWN',[KeyboardButtons.DPAD_DOWN],False,lambda : self.moveCamDown()))
    self.input_manager_.addMove(Move('LEFT',[KeyboardButtons.DPAD_LEFT],False,lambda : self.moveCamLeft()))
    self.input_manager_.addMove(Move('RIGHT',[KeyboardButtons.DPAD_RIGHT],False,lambda : self.moveCamRight()))
    
    self.input_manager_.addMove(Move('ROTATE_LEFT',[KeyboardButtons.KEY_E],False,lambda : self.rotateCamZCounterClockwise()))
    self.input_manager_.addMove(Move('ROTATE_RIGHT',[KeyboardButtons.KEY_W],False,lambda : self.rotateCamZClockwise()))
    
    self.input_manager_.addMove(Move('ZoomIn',[KeyboardButtons.KEY_A],False,lambda : self.zoomIn()))
    self.input_manager_.addMove(Move('ZoomOut',[KeyboardButtons.KEY_Q],False,lambda : self.zoomOut()))
    
    
    self.title = self.createTitle("Panda3D: " + self.name_)
    self.instructions_ = [
                          self.createInstruction(0.06, "ESC: Quit"),
                          self.createInstruction(0.12, "Up/Down: Move Camera Up/Down"),
                          self.createInstruction(0.18, "Left/Right: Move Camera Left / Rigth"),
                          self.createInstruction(0.24, "q/a: Zoom in / Zoom out"),
                          self.createInstruction(0.30, "F1: Toggle Debug"),
                          self.createInstruction(0.36, "F2: Toggle Texture"),
                          self.createInstruction(0.42, "F3: Toggle Wireframe"),
                          self.createInstruction(0.48, "F5: Screenshot")
                          ]
  
  def setupScene(self):
    
    self.__setupLevel__()
    self.__setupGameObjects__()
    
    # enable debug visuals
    self.debug_node_ = self.level_.attachNewNode(BulletDebugNode('Debug'))
    self.debug_node_.node().showWireframe(True)
    self.debug_node_.node().showConstraints(True)
    self.debug_node_.node().showBoundingBoxes(False)
    self.debug_node_.node().showNormals(True)    
    self.level_.getPhysicsWorld().setDebugNode(self.debug_node_.node())    
    self.debug_node_.hide()
    
    self.cam.reparentTo(self.level_)
    self.cam.setPos(self.level_,0, -TestGame.__CAM_ZOOM__*24, TestGame.__CAM_STEP__*25)
    
    self.camera_controller_ = CameraController(self.cam)
    
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
    StateMachine.processEvents() 
    self.input_manager_.update(dt)
    self.camera_controller_.update(dt)
    
    return task.cont
    
  def __setupLevel__(self):

    self.level_ = Level("Level1",Vec3(60,1,60))
    self.level_.reparentTo(self.render)

    # Adding platforms
    platform_details =[ 
      (-20, 4, 20, TestGame.__PLATFORM_DEPTH__, 1  ),
      (-2, 5, 10, TestGame.__PLATFORM_DEPTH__, 1  ),
      ( 4 , 1 , 16, TestGame.__PLATFORM_DEPTH__, 2),
      (-4 , 1, 10, TestGame.__PLATFORM_DEPTH__, 1),
      ( 16, 6, 30, TestGame.__PLATFORM_DEPTH__, 1),
      ( 0, -0.5, 30, TestGame.__PLATFORM_DEPTH__, 1),
      ]
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      pos = Vec3(p[0],TestGame.__PLATFORM_Y_POS,p[1])
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
      
  def rotateCamZClockwise(self):
    self.cam.setH(self.cam.getH() + TestGame.__CAM_ORIENT_STEP__)
    
  def rotateCamZCounterClockwise(self):
    self.cam.setH(self.cam.getH() + -TestGame.__CAM_ORIENT_STEP__)
      
  def zoomIn(self):
    self.cam.setY(self.cam.getY()+TestGame.__CAM_ZOOM__)

  def zoomOut(self):
    self.cam.setY(self.cam.getY()-TestGame.__CAM_ZOOM__)
    
  def toggleDebug(self):
    if self.debug_node_.isHidden():
      self.debug_node_.show()
    else:
      self.debug_node_.hide()
      
  def doReset(self):
    logging.warn("Reset Not implemented")
    pass
  
  def doScreenshot(self):
    self.screenshot('Pand3d')
      
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
      
    
    
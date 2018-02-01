import time
import logging
import sys


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
from panda3d.core import deg2Rad

from physics_platformer.state_machine import StateMachine
from physics_platformer.game_level import Level
from physics_platformer.game_level import Platform
from physics_platformer.input import Move
from physics_platformer.input import KeyboardButtons
from physics_platformer.input import KeyboardController
from physics_platformer.game_object import GameObject
from physics_platformer.camera import CameraController
from math import cos, asin, sin, acos


class TestLevel(Level):
  
  
  NUM_BOXES_ROWS = 10
  NUM_BOXES_COLUMNS = 2  
  BOX_SIDE_LENGTH = 0.4
  X_INCR = 0.6
  Z_INCR = 0.8
  START_POS = Vec3(24,0,28)
  PLATFORM_DEPTH = 10
  PLATFORM_Y = 2
    
  def __init__(self,name,min_point = Vec3(-150,-150,-50),max_point = Vec3(150,150,100)):
    Level.__init__(self,name,min_point, max_point)
    
    self.num_boxes_ = 0    
    self.setup()
    
  def setup(self):
    
    num_sectors = 6
    sector_length = 100    
    angle_incr = 360.0/num_sectors    
    angle_offset = -180
    radius = 0.5*sector_length/sin(deg2Rad(0.5*angle_incr))
    y_offset = radius*cos(deg2Rad(0.5*angle_incr))
    z_incr = 8
    logging.info("radius = " + str(radius) + ' sector length = ' + str(2*radius*sin(deg2Rad(angle_incr))) )
    
    dummy_node = NodePath('dummy-node')
    dummy_node.reparentTo(self)
    for i in range(0,num_sectors):
      
      # updating z value
      z = i*z_incr
      
      # placing dummy node
      dummy_node.clearTransform(self)
      dummy_node.setZ(self,z)
      dummy_node.setHpr(self,i*angle_incr,0,0)
      dummy_node.setY(dummy_node,-y_offset)
      dummy_node.setX(dummy_node,-0.5*sector_length)      
      
      # creating sector
      tf = dummy_node.getTransform(self)
      sector = self.addSector(tf,'sector' + str(i))
      self.__createPlatforms__(sector,i == 0) 
      self.__createBoxes__(sector)   
      
    # adding sector transitions
    sector = None
    dest_sector = None
    for i in range(0,num_sectors-1):
      
      sector = self.getSectors()[i]
      dest_sector = self.getSectors()[i+1]
      sector.connect(dest_sector,Vec3(100,0,28),True)
       
      continue
    
      if i == 0:        
        # following sector
        dest_sector = self.getSectors()[i+1]
        sector.addTransition(dest_sector,Vec3(100,0,28),True)
        
      elif i > 0 and i < num_sectors - 1:
        # following sector
        dest_sector = self.getSectors()[i+1]
        sector.addTransition(dest_sector,Vec3(100,0,28),True)
        
        # preceeding sector
        dest_sector = self.getSectors()[i-1]
        sector.addTransition(dest_sector,Vec3(0,0,20),False)
        
      else:
        # preceeding sector
        dest_sector = self.getSectors()[i-1]
        sector.addTransition(dest_sector,Vec3(0,0,20),False)
      
    dummy_node.removeNode()
      
  def __createBoxes__(self,sector):
    
    box_size = Vec3(TestLevel.BOX_SIDE_LENGTH,TestLevel.BOX_SIDE_LENGTH,TestLevel.BOX_SIDE_LENGTH)
    
    for c in range(0,TestLevel.NUM_BOXES_COLUMNS):    
      for r in range(0,TestLevel.NUM_BOXES_ROWS):     
        current_pos = TestLevel.START_POS + Vec3(r*TestLevel.X_INCR,0,c*TestLevel.Z_INCR)
           
        obj = GameObject.createBox("box"+str(self.num_boxes_),box_size,True)
        self.addGameObject(obj)
        obj.setPos(sector,current_pos) 
        obj.setHpr(sector,0,0,0)
        sector.attach(obj) 
    
    
  def __createPlatforms__(self,sector,use_first_ledge = False):
    
    # Platforms Schematic X, Z (Each new line measures 2 units and each character 2 units)
    
    '''                               
           30                                          _______
                                                      | |_16__|      ______
                                                      | |  _________|      |
                                                      | | |___22____|___14_|
                                        __________    | |___        |  |
           20        ___________       |     |    |   | |_8_|   ____|8_|  
                    |___24______|      |  12 |_10_|   |4|__    |__16___|
                      | |    __________|_____|        | |6_|   _____
                      |4|   |_____26_____|     _______|_|___  |_12__|     __________
                      |_|                     |_____30______|            |____22____|
           10           ||              ________    ____________       
                        ||             |___16___|  |            |
                        ||  |4|                    |_____28_____|
                        ||                                                                        
                        ||                                                                               
            0                                                                                            
          -20  -10    0   10   20   30   40   50   60   70   80   90   100
    '''
    
    # Platform Details [ (float left, float top, Vec3 size, Bool right_ledge, Bool left_ledge ),... ]
    depth = TestLevel.PLATFORM_DEPTH
    platform_details = [
                        (-4,20,Vec3(24,depth,2),True,use_first_ledge),
                        (0,18,Vec3(4,depth,6),False,False),
                        (4,12,Vec3(2,depth,10),True,True),
                        (12,8,Vec3(4,depth,2),True,True),
                        (12,16,Vec3(26,depth,2),False,True),
                        (46,22,Vec3(10,depth,4),True,False),
                        (34,22,Vec3(12,depth,6),False,True),
                        (34,10,Vec3(18,depth,2),True,True),
                        (48,14,Vec3(30,depth,2),True,True),
                        (58,10,Vec3(28,depth,4),True,True),
                        (64,30,Vec3(4,depth,16),False,True),
                        (68,30,Vec3(12,depth,2),True,False),
                        (68,22,Vec3(8,depth,2),True,False),
                        (68,18,Vec3(6,depth,2),True,False),
                        (72,26,Vec3(22,depth,2),False,True),
                        (82,20,Vec3(16,depth,2),False,True),
                        (80,16,Vec3(12,depth,2),True,True),
                        (92,28,Vec3(14,depth,4),True,True),
                        (92,24,Vec3( 8,depth,4),False,False),
                        (102,14,Vec3(22,depth,2),True,True)]
    
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      size = p[2]
      pos = Vec3(p[0] + size.getX()*0.5, TestLevel.PLATFORM_Y , p[1] - size.getZ()*0.5)
      right_ledge_enable = p[3]
      left_ledge_enable = p[4]
      
      platform = Platform(sector.getName() + '-' + 'platform' + str(i),size,right_ledge_enable,left_ledge_enable)
      self.addPlatform(platform)
      platform.setPos(sector,pos)
      platform.setHpr(sector,0,0,0)

class TestGame(ShowBase):
  
  __CAM_ZOOM__ =  1
  __CAM_STEP__ = 0.2
  __CAM_ORIENT_STEP__ = 4.0
  
  __BACKGROUND_IMAGE_PACKAGE__ = 'physics_platformer'
  __BACKGROUND_IMAGE_PATH__ = rospack.RosPack().get_path(__BACKGROUND_IMAGE_PACKAGE__) + '/resources/backgrounds/' + 'sky02.png'
  __BACKGROUND_POSITION__ = Vec3(0,100,0)
  __BACKGROUND_SCALE__ = 0.2 

  
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
        raise IOError("PNMImageHeader could not read file %s. Try using absolute filepaths"%(image_file.c_str()))
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
    
    self.level_ = TestLevel('ground-zero')
    self.level_.reparentTo(self.render)
    
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
      
    
    
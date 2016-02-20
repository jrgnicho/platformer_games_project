#!/usr/bin/env python
import sys
import time
import logging

from direct.showbase.ShowBase import ShowBase
from direct.controls.InputState import InputState
from direct.gui.OnscreenText import OnscreenText

from panda3d.core import AmbientLight, Filename, LColor, Mat4, BoundingVolume,\
  BoundingPlane
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
from panda3d.core import loadPrcFileData

# physics
from panda3d.bullet import BulletWorld, BulletGhostNode, BulletManifoldPoint,\
  BulletContactResult, BulletShape
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

# background image
from panda3d.core import PNMImage, PNMImageHeader, Filename
from panda3d.core import CardMaker
from panda3d.core import Texture
from panda3d.core import TextureStage
from panda3d.core import TransparencyAttrib
from rospkg import rospack

LOOP_DELAY = 0.05 # seconds
CAM_DISTANCE =  20
ROTATIONAl_SPEED = 20
BACKGROUND_IMAGE_PACKAGE = 'simple_platformer'
BACKGROUND_IMAGE_PATH = 'cplusplus_programming_background_960x800.jpg'
BACKGROUND_POSITION = Vec3(0,100,0)
BACKGROUND_IMAGE_SCALE = 0.2

# Bitmasks
SECTOR_ENTERED_BITMASK = BitMask32.bit(2)
GAME_OBJECT_BITMASK = BitMask32.bit(3)

# Sector detection
PLAYER_GHOST_DIAMETER = 0.01
SECTOR_PLANE_POS = Vec3(0,-0.15,0)
SECTOR_PLANE_SIZE = Vec3(100,0.01,40)
SECTOR_COLLISION_MARGIN = 0.001

# configure to use group-mask collision filtering mode in the bullet physics world
loadPrcFileData('', 'bullet-filter-algorithm groups-mask')

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
    
class Sector(NodePath):
  
  def __init__(self,name,physics_world):
    
    NodePath.__init__(self,name)
    self.object_nodes_ = []
    self.physics_world_ = physics_world
    
  def __del__(self):
    self.cleanup()
    
  def setup(self):
    self.setupBoxes()
    self.setupPlatforms()
    
    # setting up sector plane
    self.detection_plane_ = self.attachNewNode(BulletRigidBodyNode(self.getName() + 'plane'))
    box_shape =  BulletBoxShape(SECTOR_PLANE_SIZE/2)
    box_shape.setMargin(SECTOR_COLLISION_MARGIN)
    self.detection_plane_.node().addShape(box_shape)
    self.detection_plane_.node().setMass(0)
    self.detection_plane_.setPos(self,SECTOR_PLANE_POS)
    self.detection_plane_.node().setIntoCollideMask(SECTOR_ENTERED_BITMASK)
    self.physics_world_.attach(self.detection_plane_.node())    
    self.detection_plane_.node().clearBounds()
    
  def getSectorPlaneNode(self):
    return self.detection_plane_
  
  def cleanup(self):
    
    for obj in self.object_nodes_:
      self.physics_world_.remove(obj.node())
  
    
  def addBox(self,name,size,pos,visual):

    # Box (dynamic)
    box = NodePath(BulletRigidBodyNode(name))
    box.node().setMass(1.0)
    box.node().addShape(BulletBoxShape(size))
    box.setCollideMask(GAME_OBJECT_BITMASK)
    box.node().setLinearFactor((1,0,1))
    box.node().setAngularFactor((0,1,0))
    visual.instanceTo(box)
    box.reparentTo(self)    
    box.setPos(pos)

    self.physics_world_.attachRigidBody(box.node())
    self.object_nodes_.append(box)
    
    return box
  
    
  def setupBoxes(self):
    
    num_boxes = 20
    side_length = 0.2    
    size = Vec3(0.5*side_length,0.5*side_length,0.5*side_length)
    start_pos = Vec3(-num_boxes*side_length,0,6)
    
    box_visual = loader.loadModel('models/box.egg')
    box_visual.clearModelNodes()
    box_visual.setTexture(loader.loadTexture('models/wood.png'))
    bounds = box_visual.getTightBounds() # start of box model scaling
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = side_length/max([extents.getX(),extents.getY(),extents.getZ()])
    box_visual.setScale((scale_factor,scale_factor ,scale_factor)) 
    
    for i in range(0,num_boxes):
      box_np = self.addBox("%s-box%i"%(self.getName(),i),size,start_pos + Vec3(i*side_length,0,0),box_visual)

    start_pos = Vec3(-num_boxes*side_length,0,8)
    for i in range(0,num_boxes):
      box_np = self.addBox("%s-box %i"%(self.getName(),i),size,start_pos + Vec3(i*2*side_length,0,0),box_visual)
  
  def setupPlatforms(self):

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
    visual.setTexture(loader.loadTexture('models/iron.jpg'),1)
    
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      topleft = (p[0],p[1])
      size = Vec3(p[2],p[3],p[4])
      self.addPlatform(topleft, size,'Platform%i'%(i),visual)


  def addPlatform(self,topleft,size,name,visual):

    # Box (static)
    platform = self.attachNewNode(BulletRigidBodyNode(name))
    platform.node().setMass(0)
    platform.node().addShape(BulletBoxShape(size/2))
    platform.setPos(Vec3(topleft[0] + 0.5*size.getX(),0,topleft[1]-0.5*size.getZ()))
    platform.setCollideMask(GAME_OBJECT_BITMASK)
    local_visual = visual.instanceUnderNode(platform,name + '_visual')
    
    # Visual scaling
    bounds = local_visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    local_visual.setScale(size.getX()*scale_factor,size.getY()*scale_factor,size.getZ()*scale_factor)
    

    self.physics_world_.attachRigidBody(platform.node())
    self.object_nodes_.append(platform)

class TestApplication(ShowBase):

  def __init__(self):

    ShowBase.__init__(self)
    
    # game objects   
    self.controlled_obj_index_ = 0
    self.level_sectors_ = []
    self.controlled_objects_ = []
    
    # active objects
    self.active_sector_ = None

    self.setupRendering()
    self.setupControls()
    self.setupPhysics()
    self.clock_ = ClockObject()
    self.kinematic_mode_ = False
    
    # Task
    logging.info("TestSectors demo started")
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
    
    
    image_file = Filename(rospack.RosPack().get_path(BACKGROUND_IMAGE_PACKAGE) + '/resources/backgrounds/' + BACKGROUND_IMAGE_PATH)
    
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
    background_np.setPos(BACKGROUND_POSITION)
    background_np.setScale(BACKGROUND_IMAGE_SCALE)
  

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
    
  def processCollisions(self):
    
    contact_manifolds = self.physics_world_.getManifolds()
    for cm in contact_manifolds:      
      node0 = cm.getNode0()
      node1 = cm.getNode1()
      col_mask1 = node0.getIntoCollideMask()
      col_mask2 = node1.getIntoCollideMask()
      
      
      if (col_mask1 == col_mask2) and \
        (col_mask1 == SECTOR_ENTERED_BITMASK) and \
        self.active_sector_.getSectorPlaneNode().getName() != node0.getName():
        
        logging.info('Collision between %s and %s'%(node0.getName(),node1.getName()))
        sector = [s for s in self.level_sectors_ if s.getSectorPlaneNode().getName() == node0.getName()]
        sector = [s for s in self.level_sectors_ if s.getSectorPlaneNode().getName() == node1.getName()] + sector
        
        self.active_sector_ = sector[0]
        logging.info("Sector %s entered"%(self.active_sector_.getName()))
    
   

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
    
    # setting up collision groups
    self.physics_world_.setGroupCollisionFlag(GAME_OBJECT_BITMASK.getLowestOnBit(),GAME_OBJECT_BITMASK.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(SECTOR_ENTERED_BITMASK.getLowestOnBit(),SECTOR_ENTERED_BITMASK.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(GAME_OBJECT_BITMASK.getLowestOnBit(),SECTOR_ENTERED_BITMASK.getLowestOnBit(),False)
    

    # setting up ground
    self.ground_ = self.world_node_.attachNewNode(BulletRigidBodyNode('Ground'))
    self.ground_.node().addShape(BulletPlaneShape(Vec3(0, 0, 1), 0))
    self.ground_.setPos(0,0,0)
    self.ground_.setCollideMask(GAME_OBJECT_BITMASK)
    self.physics_world_.attachRigidBody(self.ground_.node())
    
    # creating level objects    
    self.setupLevelSectors()

    # creating controlled objects
    diameter = 0.4
    sphere_visual = loader.loadModel('models/ball.egg')

    bounds = sphere_visual.getTightBounds() # start of model scaling
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = diameter/max([extents.getX(),extents.getY(),extents.getZ()])
    sphere_visual.clearModelNodes()
    sphere_visual.setScale(scale_factor,scale_factor,scale_factor) # end of model scaling

    sphere_visual.setTexture(loader.loadTexture('models/bowl.jpg'),1)
    sphere = NodePath(BulletRigidBodyNode('Sphere'))
    sphere.node().addShape(BulletSphereShape(0.5*diameter))
    sphere.node().setMass(1.0)
    sphere.node().setLinearFactor((1,0,1))
    sphere.node().setAngularFactor((0,1,0))
    sphere.setCollideMask(GAME_OBJECT_BITMASK)
    sphere_visual.instanceTo(sphere)
    
    self.physics_world_.attachRigidBody(sphere.node())
    self.controlled_objects_.append(sphere)
    sphere.reparentTo(self.level_sectors_[0])    
    sphere.setPos(Vec3(0,0,diameter+10))
    
    # creating bullet ghost for detecting entry into other sectors
    player_ghost = sphere.attachNewNode(BulletGhostNode('player-ghost-node'))
    ghost_box_shape = BulletBoxShape(Vec3(PLAYER_GHOST_DIAMETER,PLAYER_GHOST_DIAMETER,PLAYER_GHOST_DIAMETER)/2)
    ghost_box_shape.setMargin(SECTOR_COLLISION_MARGIN)
    ghost_sphere_shape = BulletSphereShape(PLAYER_GHOST_DIAMETER*0.5)
    ghost_sphere_shape.setMargin(SECTOR_COLLISION_MARGIN)
    player_ghost.node().addShape(ghost_box_shape)
    player_ghost.setPos(sphere,Vec3(0,0,0))
    player_ghost.node().setIntoCollideMask(SECTOR_ENTERED_BITMASK)
    self.physics_world_.attach(player_ghost.node())

    # creating mobile box
    size = Vec3(0.2,0.2,0.4)
    mbox_visual = loader.loadModel('models/box.egg')
    bounds = mbox_visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    mbox_visual.setScale(size.getX()*scale_factor,size.getY()*scale_factor,size.getZ()*scale_factor)

    mbox = NodePath(BulletRigidBodyNode('MobileBox'))
    mbox.node().addShape(BulletBoxShape(size/2))
    mbox.node().setMass(1.0)
    mbox.node().setLinearFactor((1,0,1))
    mbox.node().setAngularFactor((0,1,0))
    mbox.setCollideMask(GAME_OBJECT_BITMASK)
    mbox_visual.instanceTo(mbox)    
    self.physics_world_.attachRigidBody(mbox.node())
    self.controlled_objects_.append(mbox)
    mbox.reparentTo(self.level_sectors_[0])    
    mbox.setPos(Vec3(1,0,size.getZ()+1))


  def setupLevelSectors(self):
    
    start_pos = Vec3(0,-20,0)
    
    for i in range(0,4):
      
      sector = Sector('sector' + str(i),self.physics_world_)
      sector.reparentTo(self.world_node_)
      
      sector.setHpr(Vec3(90*i,0,0))
      sector.setPos(sector,Vec3(0,-20,i*4))
      self.level_sectors_.append(sector)
      sector.setup()
      
    self.active_sector_ = self.level_sectors_[0]

  def update(self, task):

    self.clock_.tick()
    dt = self.clock_.getDt()
    self.processInput(dt)    
    self.physics_world_.doPhysics(dt, 5, 1.0/180.0)
    self.processCollisions()
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
    
    for i in range(0,len(self.controlled_objects_)):
      rb = self.controlled_objects_[i]
      self.physics_world_.removeRigidBody(rb.node())
      rb.removeNode()

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
  
  logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO)

  application = TestApplication()
  application.run()
 

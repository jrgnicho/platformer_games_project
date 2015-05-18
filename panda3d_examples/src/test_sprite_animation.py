#!/usr/bin/env python
import sys
import time

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


LOOP_DELAY = 0.05 # seconds
CAM_DISTANCE =  20
ROTATIONAl_SPEED = 10

# RUNNING hiei_run_0-7.png 8 1 80 SX1.5 SY1.5 0 0#

SPRITE_IMAGE_DETAILS = ('models/hiei_run_0-7.png',8,1,1,1,12)


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

class SpriteAnimator(NodePath):
    
  def __init__(self,name):
    NodePath.__init__(self,name)
    self.setTransparency(TransparencyAttrib.M_alpha)
    self.seq_left_ = None
    self.seq_right_ = None
    self.facing_right_ = True
    self.name_ = name
    self.size_ = (0,0)

  def getFrame(self):
    seq = self.seq_right_ if self.facing_right_ else self.seq_left_
    return seq.node().getFrame()

  def printInfo(self):
    seq = self.seq_right_ if self.facing_right_ else self.seq_left_

    print "Playing: %s"%('Yes' if seq.node().isPlaying() else 'No')
    print "Frame# %i"%(self.getFrame())
    print "Play Rate: %f"%(seq.node().getPlayRate())
    print "Sprite Size: %s"%(str(self.size_))

  def loadImage(self,file_path,cols,rows,scale_x,scale_y,frame_rate):

    # Make a filepath
    image_file = Filename(file_path)
    if image_file .empty():
        raise IOError, "File not found"
        return False

    # Instead of loading it outright, check with the PNMImageHeader if we can open
    # the file.
    img_head = PNMImageHeader()
    if not img_head.readHeader(image_file ):
        raise IOError, "PNMImageHeader could not read file %s. Try using absolute filepaths"%(file_path)
        return False

    # Load the image with a PNMImage
    full_image = PNMImage(img_head.getXSize(),img_head.getYSize())
    full_image.alphaFill(0)
    full_image.read(image_file) 

    right_image = PNMImage(img_head.getXSize(),img_head.getYSize())
    left_image = PNMImage(img_head.getXSize(),img_head.getYSize())
    right_image.copyFrom(full_image)    
    left_image.copyFrom(full_image)
    left_image.flip(True,False,False)

    # storing individual sprite size
    self.size_ = (right_image.getReadXSize()/cols,right_image.getReadYSize()/rows)

    self.seq_right_ = self.attachNewNode(self.createSequenceNode(self.name_ + '_right_seq',right_image,cols,rows,scale_x,scale_y,frame_rate))
    self.seq_left_ = self.attachNewNode(self.createSequenceNode(self.name_ + '_left_seq',left_image,cols,rows,scale_x,scale_y,frame_rate))

    right_image.clear()
    left_image.clear()
    full_image.clear()

    self.faceRight(True)      

    return True

  def createSequenceNode(self,name,img,cols,rows,scale_x,scale_y,frame_rate):
    
    seq = SequenceNode(name)
    w = int(img.getXSize()/cols)
    h = int(img.getYSize()/rows)

    counter = 0
    for i in range(0,cols):
      for j in range(0,rows):
        sub_img = PNMImage(w,h)
        sub_img.addAlpha()
        sub_img.alphaFill(0)
        sub_img.fill(1,1,1)
        sub_img.copySubImage(img ,0 ,0 ,i*w ,j*h ,w ,h)

        # Load the image onto the texture
        texture = Texture()        
        texture.setXSize(w)
        texture.setYSize(h)
        texture.setZSize(1)    
        texture.load(sub_img)
        texture.setWrapU(Texture.WM_border_color) # gets rid of odd black edges around image
        texture.setWrapV(Texture.WM_border_color)
        texture.setBorderColor(LColor(0,0,0,0))

        cm = CardMaker(name + '_' + str(counter))
        cm.setFrame(-0.5*scale_x,0.5*scale_x,-0.5*scale_y,0.5*scale_y)
        card = NodePath(cm.generate())
        seq.addChild(card.node(),counter)
        card.setTexture(texture)
        sub_img.clear()
        counter+=1
    
    seq.setFrameRate(frame_rate)
    print "Sequence Node %s contains %i frames of size %s"%(name,seq.getNumFrames(),str((w,h)))
    return seq   

  def nextFrame(self) :
    seq = self.seq_right_ if self.facing_right_ else self.seq_left_
    f = seq.node().getFrame()+1 
    if f >= seq.node().getNumFrames(): f = 0
    seq.node().pose(f)

  def faceRight(self,face_right):

    if face_right: 
      self.seq_left_.removeNode()
      self.seq_right_.reparentTo(self)

      # toggle animation
      #self.seq_left_.node().stop()
      #self.seq_right_.node().loop(True)

    else:
      self.seq_right_.removeNode()
      self.seq_left_.reparentTo(self)

      # toggle animation
      #self.seq_right.node().stop()
      #self.seq_left_.node().loop(True)

    self.facing_right_ = face_right

    seq = self.seq_right_ if self.facing_right_ else self.seq_left_
    seq.node().loop(True,0,seq.node().getNumFrames()-1)
    

class TestApplication(ShowBase):

  def __init__(self):

    ShowBase.__init__(self)

    self.setupRendering()
    self.setupControls()
    self.setupPhysics()
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
    self.accept('k',self.toggleKinematicMode)
    self.accept('p',self.printInfo)
    self.accept('q',self.zoomIn)
    self.accept('a',self.zoomOut)

    # Inputs (Polling)
    self.input_state_ = InputState()
    self.input_state_.watchWithModifiers("right","arrow_right")
    self.input_state_.watchWithModifiers('left', 'arrow_left')
    self.input_state_.watchWithModifiers('jump', 'arrow_up')
    self.input_state_.watchWithModifiers('stop', 'arrow_down')
    self.input_state_.watchWithModifiers('roll_right', 'c')
    self.input_state_.watchWithModifiers('roll_left', 'z')
    self.input_state_.watchWithModifiers('roll_stop', 'x')

    self.title = addTitle("Panda3D: Sprite Animation")
    self.inst1 = addInstructions(0.06, "ESC: Quit")
    self.inst2 = addInstructions(0.12, "Up/Down: Jump/Stop")
    self.inst3 = addInstructions(0.18, "Left/Right: Move Left / Move Rigth")
    self.inst4 = addInstructions(0.24, "z/x/c : Rotate Left/ Rotate Stop / Rotate Right")
    self.inst5 = addInstructions(0.30, "n: Select Next Character")
    self.inst6 = addInstructions(0.36, "k: Toggle Kinematic Mode")
    self.inst7 = addInstructions(0.42, "q/a: Zoom in / Zoom out")
    self.inst7 = addInstructions(0.48, "p: Print Info")

  def printInfo(self):
    self.sprt_animator_.printInfo()

  def setupPhysics(self):

    # setting up physics world and parent node path 
    self.physics_world_ = BulletWorld()
    self.world_node_ = self.render.attachNewNode('world')
    self.cam.reparentTo(self.world_node_)
    self.physics_world_.setGravity(Vec3(0, 0, -9.81))

    self.debug_node_ = self.world_node_.attachNewNode(BulletDebugNode('Debug'))
    self.debug_node_.show()
    self.debug_node_.node().showWireframe(True)
    self.debug_node_.node().showConstraints(True)
    self.debug_node_.node().showBoundingBoxes(False)
    self.debug_node_.node().showNormals(True)

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

    """
    # creating boxes
    box_visual = loader.loadModel('models/box.egg')
    box_visual.clearModelNodes()
    box_visual.setTexture(loader.loadTexture('models/wood.png'))
    
    bounds = box_visual.getTightBounds() # start of box model scaling
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = side_length/max([extents.getX(),extents.getY(),extents.getZ()])
    box_visual.setScale((scale_factor,scale_factor ,scale_factor)) # end of box model scaling

    for i in range(0,20):
      self.addBox("name %i"%(i),size,start_pos + Vec3(i*side_length,0,0),box_visual)

    start_pos = Vec3(-num_boxes*side_length,0,8)
    for i in range(0,20):
      self.addBox("name %i"%(i),size,start_pos + Vec3(i*2*side_length,0,0),box_visual)
    """

    # creating sprite animator
    sprt_animator = SpriteAnimator('hiei_run')            
    if not sprt_animator.loadImage(SPRITE_IMAGE_DETAILS[0], # file path
      SPRITE_IMAGE_DETAILS[1], # columns
      SPRITE_IMAGE_DETAILS[2], # rows
      SPRITE_IMAGE_DETAILS[3], # scale x
      SPRITE_IMAGE_DETAILS[4], # scale y
      SPRITE_IMAGE_DETAILS[5]): # frame rate
      print "Error loading image %s"%(SPRITE_IMAGE_DETAILS[0])
      sys.exit(1)
    self.sprt_animator_ = sprt_animator

    # creating Mobile Character Box
    size = Vec3(0.5,0.2,1)
    mbox_visual = loader.loadModel('models/box.egg')
    bounds = mbox_visual.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = 1/max([extents.getX(),extents.getY(),extents.getZ()])
    mbox_visual.setScale(size.getX()*scale_factor,size.getY()*scale_factor,size.getZ()*scale_factor)

    mbox = self.world_node_.attachNewNode(BulletRigidBodyNode('CharacterBox'))
    mbox.node().addShape(BulletBoxShape(size/2))
    mbox.node().setMass(1.0)
    mbox.node().setLinearFactor((1,0,1))
    mbox.node().setAngularFactor((0,1,0))
    mbox.setCollideMask(BitMask32.allOn())
    mbox_visual.instanceTo(mbox)
    mbox_visual.hide()
    mbox.setPos(Vec3(1,0,size.getZ()+1))

    bounds = sprt_animator.getTightBounds()
    extents = Vec3(bounds[1] - bounds[0])
    scale_factor = size.getZ()/extents.getZ()
    sprt_animator.setScale(scale_factor,1,scale_factor)
    sprt_animator.reparentTo(mbox)
    bounds = sprt_animator.getTightBounds()
    print "Sprite Animator bounds %s , %s"%(str(bounds[1]),str(bounds[0]))
    
    self.physics_world_.attachRigidBody(mbox.node())
    self.object_nodes_.append(mbox)
    self.controlled_objects_.append(mbox)

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
    for i in range(0,len(platform_details)):
      p = platform_details[i]
      topleft = (p[0],p[1])
      size = Vec3(p[2],p[3],p[4])
      self.addPlatform(topleft, size,'Platform%i'%(i))


  def addPlatform(self,topleft,size,name):

    # Visual
    visual = loader.loadModel('models/box.egg')
    visual.setTexture(loader.loadTexture('models/iron.jpg'))
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
    self.updateCamera()
  
    #self.sprt_animator_.nextFrame()
    #self.sprt_animator_.printInfo()

    

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

  def zoomIn(self):
    global CAM_DISTANCE
    CAM_DISTANCE-=4

  def zoomOut(self):
    global CAM_DISTANCE
    CAM_DISTANCE+=4

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
 

from physics_platformer.sprite import Sprite
from physics_platformer.sprite import SpriteGroup
from physics_platformer.sprite import SpriteAnimator
from panda3d.core import SequenceNode
from panda3d.core import Texture
import logging

class AnimationDetails(object):
  
  def __init__(self):
    
    self.sprite_group_left = None
    self.sprite_group_right = None
    self.collision_boxes = []
    self.hit_boxes =[]

class AnimationActor(SpriteAnimator):
  
  def __init__(self,name):
    SpriteAnimator.__init__(self,name)
    
    self.collision_body_ = None # bullet rigid body that contains the collision boxes
    self.hit_body_ = None # bullet ghost node containing hit boxes
    self.constraint_joint_ = None # bullet constraints that connects the collision body to its parent
    
  def getCollisionBody(self):
    return self.collision_body_
  
  def getGhostBody(self):
    """
    Returns ghost body used for attacks
    """
    return self.hit_body_
    
  def loadAnimationSprites(self,sprites_right, sprites_left,framerate,scale):
    """
    loadAnimationSprites
      Loads Sprites for the right and left animations
      Inputs:
      - sprites_right: list[Sprite] list of images for the right side
      - sprites_left: list[Sprite] list of images for the left side
      - framerate: (double) 
      - scale: (Vec3) Only the x and z values are used 
    """
    
    if (len(sprites_right) == 0) or (len(sprites_left) == 0):
      logging.error("ERROR: Found empty image list")
      return False
    
    if len(sprites_right) != len(sprites_left):
      logging.error("Unequal number of images for the left and right side")
      return False
    
    # storing individual sprite size
    w = sprites_right[0].getXSize() # assumes that all images in the in 'images' array are the same size
    h = sprites_right[0].getYSize()
    self.size_ = (w,h) # image size in pixels
    
    self.seq_right_ = self.__createAnimationSequence__(self.getName() + '-right-seq',sprites_right,frame_rate)
    self.seq_left_ = self.__createAnimationSequence__(self.getName()+ '-left-seq',sprites_left,frame_rate)
    self.node().addStashed(self.seq_right_)
    self.node().addStashed(self.seq_left_)
    
    self.setScale(Vec3(scale.getX(),1,scale.getZ()))
    self.faceRight(True)     
    
    return True
  
  def __createAnimationSequence__(self,name,sff_images,framerate):
    """
      Creates the sequence node that plays these images
    """
    seq = SequenceNode(name)
    
    for i in range(0,len(sff_images)):
        
        txtr = sff_images[i]
        
        w = txtr.getXSize() 
        h = txtr.getYSize()       
        
        # creating CardMaker to hold the texture
        cm = CardMaker(name +    str(i))
        cm.setFrame(0,w,-h,0)  # This configuration places the image's topleft corner at the origin
        card = NodePath(cm.generate())            
        card.setTexture(txtr)
        seq.addChild(card.node(),i)
        
        # offseting image
        card.setPos(Vec3(txtr.axisx,0,txtr.axisy))
     
    seq.setFrameRate(framerate)           
    print "Sequence Node %s contains %i imagese of size %s and card size of %s"%(name,seq.getNumFrames(),str((w,h)),str((cw,ch)))        
    return seq     
    
    
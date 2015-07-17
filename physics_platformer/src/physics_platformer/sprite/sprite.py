from StringIO import StringIO
from PIL import Image
from panda3d.core import PNMImage, StringStream
from panda3d.core import Texture
from panda3d.core import LColor

class Sprite(Texture):
  """
  This class extends panda3d's Texture class by adding members that are associated with a sprite image
  created with the Fighter Factory 3 software.  These extra members allow grouping the sprites into animation actions
  and also provide information about the location of the image relative to a known reference in the character coordinate frame
  """
  
  def __init__(self):
    Texture.__init__(self)
    
    self.axisx = 0 # offset distance to the right side of the sprite from the origin. X+ is to the right
    self.axisy = 0 # offset distance to the top side of the sprite from the origin. Y+ is up
    self.group = 0
    self.no = 0
    
    self.hit_boxes = []
    self.collision_boxes = []
    
    
    
class SpriteGroup(object):
  
  def __init__(self,group_no):
    """
    Container for Sprites
    """
    self.images_dict_ = {}
    self.group_no_ = group_no
    
  def isEmpty(self):    
    return len(self.images_dict_) == 0
  
  def addSprite(self,sff_im):    
    sff_im.group = self.group_no_
    self.images_dict_[sff_im.no] = sff_im
    
  def setSprites(self,sff_images):
    for im in sff_images:
      self.addSprite(im)
      
  def getSprite(self,im_no):
    if self.images_dict_.has_key(im_no):
      return self.images_dict_[im_no]
    else:
      return None
    
  def getSprites(self):
    return self.images_dict_.values()
    
  def hasSprite(self,im_no):
    return self.images_dict_.has_key(im_no)
  
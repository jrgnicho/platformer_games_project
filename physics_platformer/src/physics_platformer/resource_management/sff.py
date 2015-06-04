from physic_platformer.resource_management.sff_support import *
from panda3d.core import Texture

class SFFSprite(Texture):
  
  def __init__(self):
    Texture.__init__(self)
    
    self.axisx = 0 # offset distance to the right side of the sprite from the origin. X+ is to the right
    self.axisy = 0 # offset distance to the top side of the sprite from the origin. Y+ is up
    self.group = 0
    self.no = 0
    
class SFFSpriteGroup(object):
  
  def __init__(self,group_no):
    """
    Container for SFFSprites
    """
    self.images_dict_ = {}
    self.group_no_ = group_no
    
  def isEmpty(self):    
    return len(self.images_dict_) == 0
  
  def addImage(self,sff_im):    
    sff_im.group = self.group_no_
    self.images_dict_[sff_im.no] = sff_im
    
  def setImages(self,sff_images):
    for im in sff_images:
      self.addImage(im)
      
  def getImage(self,im_no):
    if self.images_dict_.has_key(im_no):
      return self.images_dict_[im_no]
    else:
      return None
    
  def getImages(self):
    return self.images_dict_.values()
    
  def hasImage(self,im_no):
    return self.images_dict_.has_key(im_no)
  
  class SFFLoader(object):
    
    def __init__(self):
      
      self.groups_dict_ = {}
      
    def getImage(self,group_no,im_no):
      
      pass
    
    def __loadToGroup__(self,group_no):
      pass
    
from physics_platformer.resource_management.sff_support import *
from physics_platformer.sprite import Sprite, SpriteGroup
from io import StringIO
from PIL import Image
from panda3d.core import PNMImage, StringStream
from panda3d.core import Texture
from panda3d.core import LColor
import logging
import sys
import os

  
class SFFLoader(object):
  
  def __init__(self):      
    self.groups_dict_ = {}
    
  def hasGroup(self, group_no):
    return group_no in self.groups_dict_
    
  def loadSff(self,filename,groups = []):
    """
      Loads sprite images from an sff file
      Inputs:
      - filename: (String) Path to sff file
      - groups: ([int]) indices to the groups in the sff whose images will be loaded
    """
    
    load_all = (len(groups)==0)
    return self.__parseSff__(load_all,groups)
  
  def getSprite(self,group_no,im_no,right_side = True):
    
    if self.hasGroup(group_no):        
      group_pair = self.groups_dict_[group_no]
      group = group_pair[0] if right_side else group_pair[1]
      
      return group.getSprite(im_no)
    else:
      return None
    
  def getSprites(self,group_no,right_side = True):
    
    if self.hasGroup(group_no):        
      group_pair = self.groups_dict_[group_no]
      group = group_pair[0] if right_side else group_pair[1]        
      return group.getSprites()
    else:
      return None
    
  
  
  def __parseSff__(self,filename,load_all, groups = []):
    
    # Opening file
    if os.path.exists(filename):
      logging.error("SFF file %s was not found"%(filename))
      return False
    
    if not filename.lower().endswith('.sff'):
      logging.error("File %s is not an .sff image")
      return False
    
    
    fh = open(filename, 'rb')
    header = sff1_file.parse(fh.read(512))
    
    next_subfile = header.next_subfile
    count = 0

    while next_subfile and count < header.image_total:
        fh.seek(next_subfile)
        subfile = sff1_subfile_header.parse(fh.read(32))
        next_subfile = subfile.next_subfile
  
        try:
            buff = StringIO(fh.read(subfile.length))
            image = Image.open(buff)
            
            buff = StringIO()
            image.save(buff,'PNG')
            pnm_img = PNMImage(image.size[0],image.size[1])
            pnm_img.alphaFill(0)
            
            if not pnm_img.read(StringStream(buff.getvalue()), "i.png"):
              logging.error("Failed to read from buffer, invalid image found in sff file")
              return False         
  
            logging.debug("Image Group: %i, no: %i, size: %i x %i ,offset: (%i , %i), palette %i"%(subfile.groupno,subfile.imageno, 
              image.size[0],image.size[1],subfile.axisx,subfile.axisy,subfile.palette))
            
            # Check if group is requested              
            if not load_all:
              if groups.count(subfile.groupno) == 0:
                continue # skip this group
            
            # storing image
            if not self.hasGroup(subfile.groupno):
              # create left and right groupos
              self.groups_dict_[subfile.groupno] = (SpriteGroup(subfile.groupno),SpriteGroup(subfile.groupno))
                     
            group_pair = self.groups_dict_[subfile.groupno]
            group_right = group_pair[0]
            group_left = group_pair[1]
            
            group_right.addSprite(self.__makeSprite__(pnm_img,subfile,False))
            group_left.addSprite(self.__makeSprite__(pnm_img,subfile,True))              
            
        except IOError:
            loggin.error("ioerror while reading image in group %i and no %i"%( subfile.groupno, subfile.imageno))
            return False
              
        count+=1
        
    return True
  
  @staticmethod
  def __makeSprite__(self,pnm_img,subfile,flip):  
    
    img  = None
    if flip:
      img = PNMImage(pnm_img.getXSize(),pnm_img.getYSize())  
      img.copyFrom(pnm_img)        
      img.flip(True ,False,False)    
    else:
      img = pnm_img                
              
    sff_image = Sprite()     
    sff_image.setXSize(img.getXSize())
    sff_image.setYSize(pnm_img.getYSize())
    sff_image.setZSize(1)    
    sff_image.axisx = -subfile.axisx if (not flip ) else subfile.axisx
    sff_image.axisy = subfile.axisy
    sff_image.group = subfile.groupno
    sff_image.no = subfile.imageno
    sff_image.load(img)
    sff_image.setWrapU(Texture.WM_border_color) # gets rid of odd black edges around image
    sff_image.setWrapV(Texture.WM_border_color)
    sff_image.setBorderColor(LColor(0,0,0,0))
    
    return sff_image
          
      
    
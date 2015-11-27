from panda3d.core import PNMImage, PNMImageHeader
from panda3d.core import Texture
from panda3d.core import LColor
from physics_platformer.sprite import Sprite
from physics_platformer.sprite import SpriteGroup
import os
import logging
import re

"""
Module that provides support for loading multiple files generated from the figther factory software
"""

class FFELoader(object):
  
  __EXTENSION__ = '.ffe'
  __SPRITE_HEADER__ = '(\[SpriteDef\])'
  __GROUP_FIELD__ = 'group =\s*(\d+)'
  __IMAGE_FIELD__ = 'image =\s*(\d+)'
  __XAXIS_FIELD__ = 'xaxis =\s*(\d+)'
  __YAXIS_FIELD__ = 'yaxis =\s*(\d+)'
  __FILE_FIELD__ = 'file =\s*(\d+-\d+\.png)'
  
  class SpriteDetails(object):
    
    def __init__(self):
      
      self.group_no = 0
      self.image_no = 0
      self.axisx = 0
      self.axisy = 0
      self.im_file = ''
  
  def __init__(self):   
    
    self.groups_dict_ = {}    
    self.logger_ = logging.getLogger(__name__)
    self.logger_.setLevel( level= logging.INFO)
        
  def hasGroup(self, group_no):
    return self.groups_dict_.has_key(group_no)
    
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
  
  def load(self,filename, groups = []):
    """
      load(string filename,list[int] groups) 
      Loads sprites from an ffe file
      Inputs:
      - filename: Path to the file
      - groups: list of groups to be loaded
    """
    load_all_groups = (len(groups) == 0)
    
    # openning file
    if not ( os.path.exists(filename) and filename.endswith(FFELoader.__EXTENSION__)):
      logging.error("File %s is invalid"%(filename))
      return False
      
    dirname, junk = os.path.split(os.path.abspath(filename))
      
    f = open(filename,'r')
    lines = f.readlines()    
    self.logger_.debug("File %s contains %i lines"%(filename,len(lines)))
    
    # image group containers
    group_right = None
    group_left = None    
    sd = FFELoader.SpriteDetails()
    
    line_counter = -1        
    while line_counter < len(lines)-1:
      
      # finding Sprite header
      max_searches = 8
      search_count = 0
      save = False
      line_counter+=1
            
      val = self.__checkMatch__(lines[line_counter], FFELoader.__SPRITE_HEADER__)
      if val is not None:
        sd = FFELoader.SpriteDetails()
        continue
      
      val = self.__checkMatch__(lines[line_counter], FFELoader.__GROUP_FIELD__)
      if val is not None:
        sd.group_no = int(val)
        continue
      
      val = self.__checkMatch__(lines[line_counter], FFELoader.__IMAGE_FIELD__)
      if val is not None:
        sd.image_no = int(val)
        continue
      
      val = self.__checkMatch__(lines[line_counter], FFELoader.__XAXIS_FIELD__)
      if val is not None:
        sd.axisx = int(val)
        continue
      
      val = self.__checkMatch__(lines[line_counter], FFELoader.__YAXIS_FIELD__)
      if val is not None:
        sd.axisy = int(val)
        continue
      
      val = self.__checkMatch__(lines[line_counter], FFELoader.__FILE_FIELD__)
      if val is not None:
        sd.im_file = dirname + '/' + val
        save = True
      
      if save:
        if load_all_groups:
          group_right, group_left = self.__createGroupPair__(sd.group_no)
        else:          
          if groups.count(sd.group_no) == 0:
            logging.warn("Skipping unrequested group %i"%(sd.group_no))
            continue                    
          group_right, group_left = self.__createGroupPair__(sd.group_no)
          
        right_sprt, left_sprt = FFELoader.__loadSpritePair__(sd)
        
        if right_sprt is None or left_sprt is None:
          logging.error("Sprite %s  was not found"%(sd.im_file))
          return False
        
        group_right.addSprite(right_sprt)
        group_left.addSprite(left_sprt)        
                
        self.logger_.debug("Stored Image: group = %i, image# = %i, axisx = %i, axisy = %i, file = %s"%(sd.group_no,
                                                                                           sd.image_no,
                                                                                           sd.axisx,
                                                                                           sd.axisy,
                                                                                           sd.im_file))

    
    return len(self.groups_dict_ ) > 0   
      
      
  def __readLine__(self,line,field_text):
    start = line.find(field_text)
    end = start + len(field_text)
    if start != -1:
      return line[end:].rstrip().replace('\n','')
    
    return ''
  
  def __checkMatch__(self,line,key):
    match = re.search(key,line)
    val = None
    if match is not None:
      val = match.group(1)
      
    return val
    
  
  def __createGroupPair__(self,group_no):
    
    if not self.groups_dict_.has_key(group_no):
      self.groups_dict_[group_no] = (SpriteGroup(group_no),SpriteGroup(group_no))
    
    return self.groups_dict_[group_no] 
  
  @staticmethod
  def __loadSpritePair__(sprite_details):  
    
    image_file = sprite_details.im_file
    img_head = PNMImageHeader()
    if not img_head.readHeader(image_file ):
        logging.error( "PNMImageHeader could not read file %s. Try using absolute filepaths"%(image_file))
        return (None,None)

    # Load the right side image as a PNMImage
    right_img = PNMImage(img_head.getXSize(),img_head.getYSize())
    right_img.alphaFill(0)
    right_img.read(image_file)
    
    # Flip to get the left side image
    left_img = PNMImage(right_img.getXSize(),right_img.getYSize())  
    left_img.copyFrom(right_img)        
    left_img.flip(True ,False,False) 
    
    images = [(right_img,False),(left_img,True)]
    sprites = []
    
    for entry in images:      
       
      img = entry[0]
      flip = entry[1]        
      sprite = Sprite()     
      sprite.setXSize(img.getXSize())
      sprite.setYSize(img.getYSize())
      sprite.setZSize(1)    
      sprite.axisx = -sprite_details.axisx if (not flip ) else sprite_details.axisx
      sprite.axisy = sprite_details.axisy
      sprite.group = sprite_details.group_no
      sprite.no = sprite_details.image_no
      sprite.load(img)
      sprite.setWrapU(Texture.WM_border_color) # gets rid of odd black edges around image
      sprite.setWrapV(Texture.WM_border_color)
      sprite.setBorderColor(LColor(0,0,0,0))
      
      sprites.append(sprite)
    
    return (sprites[0],sprites[1])
     
   
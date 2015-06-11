from panda3d.core import PNMImage, PNMImageHeader
from panda3d.core import Texture
from panda3d.core import LColor
from physics_platformer.sprite import Sprite
from physics_platformer.sprite import SpriteGroup
from construct import *
import os
import logging

"""
Module that provides support for loading multiple files generated from the figther factory software
"""

class FFELoader(object):
  
  __EXTENSION__ = '.ffe'
  __SPRITE_HEADER__ = '[SpriteDef]'
  __GROUP_FIELD__ = 'group = '
  __IMAGE_FIELD__ = 'image = '
  __XAXIS_FIELD__ = 'xaxis = '
  __YAXIS_FIELD__ = 'yaxis = '
  __FILE_FIELD__ = 'file = '
  
  class SpriteDetails(object):
    
    def __init__(self):
      
      self.group_no = 0
      self.image_no = 0
      self.axisx = 0
      self.axisy = 0
      self.im_file = ''
  
  def __init__(self):   
    
    self.groups_dict_ = {}
  
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
      
    dirname, junk = os.path.split(os.path.abspath(filename))
      
    f = open(filename,'r')
    lines = f.readlines()    
    logging.debug("File %s contains %i lines"%(filename,len(lines)))
    
    # image group containers
    group_right = None
    group_left = None    
    sd = FFELoader.SpriteDetails()
    
    line_counter = 0    
    
    while line_counter < len(lines):
      
      # finding Sprite header
      line = lines[line_counter]
      pos = line.find(FFELoader.__SPRITE_HEADER__) 
      if pos != -1:
        
        line_counter+=1
        sd.group_no = int(self.__readLine__(lines[line_counter], FFELoader.__GROUP_FIELD__))
        line_counter+=1
        sd.image_no = int(self.__readLine__(lines[line_counter], FFELoader.__IMAGE_FIELD__))
        line_counter+=1
        sd.axisx = int(self.__readLine__(lines[line_counter], FFELoader.__XAXIS_FIELD__))
        line_counter+=1
        sd.axisy = int(self.__readLine__(lines[line_counter], FFELoader.__YAXIS_FIELD__))
        line_counter+=3
        sd.im_file = self.__readLine__(lines[line_counter], FFELoader.__FILE_FIELD__)
        sd.im_file = dirname + '/' + sd.im_file

        if load_all_groups:
          group_right, group_left = self.__createGroupPair__(sd.group_no)
          pass
        else:          
          if groups.count(sd.group_no) == 0:
            continue                     
          group_right, group_left = self.__createGroupPair__(sd.group_no)
          
        right_sprt, left_sprt = FFELoader.__loadSpritePair__(sd)
        
        if right_sprt == None:
          return False
        
        group_right.addSprite(right_sprt)
        group_left.addSprite(left_sprt)        
                
        logging.debug("Image: group = %i, image# = %i, axisx = %i, axisy = %i, file = %s"%(sd.group_no,
                                                                                           sd.image_no,
                                                                                           sd.axisx,
                                                                                           sd.axisy,
                                                                                           sd.im_file))
        
        
      line_counter+=1
        
      
      
  def __readLine__(self,line,field_text):
    start = line.find(field_text)
    end = start + len(field_text)
    if start != -1:
      return line[end:].rstrip().replace('\n','')
    
    return ''
  
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
      
        
    
    
  
class AIRLoader(object):
  
  def __init__(self):
    pass
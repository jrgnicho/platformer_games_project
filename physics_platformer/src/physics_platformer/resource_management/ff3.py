from panda3d.core import PNMImage, PNMImageHeader
from panda3d.core import Texture
from panda3d.core import LColor
from physics_platformer.sprite import Sprite
from physics_platformer.sprite import SpriteGroup
from physics_platformer.geometryd2d import Box2D
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
  
  __EXTENSION__ = ".air"
  __ANIMATION_NAME__ = '^; (.+)'
  __BEGIN_HEADER__ = '\[Begin Action ([0-9]+)\]'
  __BOX_INFO__ = '([-]?[0-9]+), '*3 + '$([-]?[0-9]+)' # left, top, right, bottom (x+ from left to right and y+ from top to bottom)
  __COLLISION_BOX_STATIC_LIST__ = 'Clsn2Default: ([1-9]+)'
  __COLLISION_BOX_LIST__ = 'Clsn2: ([1-9]+)'
  __COLLISION_BOX_ENTRY__ = 'Clsn2\[(0-9)] = '
  __HIT_BOX_LIST__ = 'Clsn1: ([1-9)+)'
  __HIT_BOX_ENTRY__ = 'Clsn1\([0-9]+)\] = '
  __SPRITE_ENTRY__ = '[,| ]*([0-9]+)'*5 #  group, sprite_no, offsetx, offsety, time(framerate) -> 50,1, 0,0, 6
  
  def __init__(self):
    pass
  
  def load(self,filename):
    
    # openning file
    if not ( os.path.exists(filename) and filename.endswith(AIRLoader.__EXTENSION__)):
      logging.error("File %s is invalid"%(filename))
      return False
    
    f = open(filename,'r')
    lines = f.readlines()
    
    linecount = 0
    anim_name =''
    anim_id = 0
    static_col_boxes = []
    col_boxes_dict = {}
    hit_boxes_dict ={}
    anim_sprites = [] # list of tuples (group_no, image_no)
    anim_framerate = 10
    
    parse_animation = False
    while linecount < len(lines):   
      
      line = lines[linecount]      
      linecount+=1     
      
      m = re.search(AIRLoader.__ANIMATION_NAME__,line)
      if m is not None:
        anim_name = m.group(1)
        
        # finding header
        line = lines[linecount]          
        linecount+=1     
         
        m = re.search(AIRLoader.__BEGIN_HEADER__,line)
        if m is not None:
          anim_id  = int(m.group(1))
        else:
          logging.error("Animation header was not found");
          return False           
        
        parse_animation = True
      
        while parse_animation:  
               
          line = lines[linecount]          
          linecount+=1  
          
          # find Default Collision Boxes
          m = re.search(AIRLoader.__COLLISION_BOX_STATIC_LIST__,line)
          if m is not None:
            static_col_boxes = int(m.group(1))
            
          # find Hit Boxes
          m = re.search(AIRLoader.__HIT_BOX_LIST__,line)
          if m is not None:
            box_count = int(m.group(1))
            linecount+=1
            box_list,linecount = self.__parseBoxList__(AIRLoader.__HIT_BOX_ENTRY__, lines, linecount)
            
            if (len(box_list) != box_count ) :
              logging.error("Size of hit box list is incorrect")
              return False
            
            linecount+=1
            sprite_entry = self.__parseSpriteEntry__(lines, linecount)
            if sprite_entry is None:
              logging.error("Sprite entry corresponding to hit boxes was not found")
              return False
            
            
            
            
            
            
        
  def __parseCollisionBoxList__(self,lines,linecount):
    return self.__parseBoxList__(AIRLoader.__COLLISION_BOX_ENTRY__, lines, linecount)
  
  def __parseHitBoxList__(self,lines,linecount):    
    return self.__parseBoxList__(AIRLoader.__HIT_BOX_ENTRY__, lines, linecount)
      
  def __parseBoxList__(self,token_expr,lines,linecount):
    
    proceed = True
    box_list = []
    
    while proceed:
      line = lines[linecount]
      m = re.search(token_expr,line)
      
      if m is None:
        proceed = False
        break
      
      # parsing box coordinates
      start = m.end()
      b = re.search(AIRLoader.__BOX_INFO__,line[start:])
      left = float(b.group(1))
      top = float(-b.group(2))
      right = float(b.group(3))
      bottom = float(-b.group(4))
      
      w = abs(right - left)
      h = abs(top - bottom)
      cx = left + w*0.5
      cy = bottom + h*0.5
      
      box = Box2D(w,h,(cx,cy))
      box_list.append(box)
      linecount+=1      
      proceed = True
      
    return (box_list,linecount)
  
  def __parseSpriteEntry__(self,lines,linecount):
    
    group_no = 0
    im_no = 0
    offsetx = 0
    offsety = 0
    delay = 0
    
    line = lines[linecount]
    m = re.search(AIRLoader.__SPRITE_ENTRY__,line)
    if m is None:
      return (None,linecount)
    
    group_no = int(m.group(1))
    im_no = int(m.group(2))
    offsetx = int(m.group(3))
    offsety = int(m.group(4))
    delay = int(m.group(5))
    
    linecount+=1
    return ( (group_no,im_no,offsetx,offsety,delay) , linecount)
    
         
      
      
      
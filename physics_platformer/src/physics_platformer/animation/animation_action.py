from physics_platformer.geometry2d import Box2D
import re
from construct import *
import os
import logging
   
      
class AnimationElement(object):
  """
  Class that stores the data of an "Animation Element" as defined in a M.U.G.E.N AIR file (http://elecbyte.com/wiki/index.php/AIR)
  """
  
  def __init__(self):
    self.group_no = 0
    self.im_no =0
    self.hit_boxes = []
    self.collision_boxes = []   
    self.game_ticks = 0 # Number of ticks that this image will be displayed
    
  def __str__(self):
    hit_str =''
    for b in self.hit_boxes:
      hit_str += '\t' + str(b) + '\n' 
    
    col_str = ''
    for b in self.collision_boxes:
      col_str+= '\t' + str(b) + '\n' 
    
    s = """
        Animation Element:
          group no: %i
          im no: %i
          hit boxes: %i 
          %s
          collision boxes: %i
          %s
          game ticks: %i
    """%(self.group_no,self.im_no,len(self.hit_boxes),hit_str,len(self.collision_boxes),col_str,self.game_ticks)
    return s
       
class AnimationAction(object):
  """
  Class that stores the animation elements and other relevant data associated with a "Animation Action" as define in a M.U.G.E.N Air file
  """
  def __init__(self,name = ''):
    self.name = name
    self.id = 0
    self.loopstar = -1
    self.framerate = 0
    self.static_collision_boxes = []
    self.static_hit_boxes = []
    self.animation_elements =[]
    self.sprites_left = []
    self.sprites_right = []
    
  def __str__(self):
    hit_str = ''
    for b in self.static_hit_boxes:
      hit_str+= '\t' + str(b) + '\n' 
      
    col_str = ''
    for b in self.static_collision_boxes:
      col_str += '\t' + str(b) + '\n'
      
    elmt_str = ''
    for elmt in self.animation_elements:
      elmt_str += '\t' + str(elmt) + '\n'
    
    s = """
    Animation Action: %s
      id : %i
      framerate : %i
      collision boxes : %i
      %s
      hit boxes: %i
      %s
      animation elements: 
        %s
    """%(self.name,self.id,self.framerate,len(self.static_collision_boxes),col_str,len(self.static_hit_boxes),hit_str,elmt_str)
    
    return s
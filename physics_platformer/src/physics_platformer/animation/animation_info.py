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
    self.hit_boxes = [] # boxes to check if the character's attack hits the oponent
    self.damage_boxes = [] # boxes to check if the incoming attack hits the character
    self.game_ticks = 0 # Number of clock ticks that this image will be displayed.  The corresponding time 
                        # that the image is show can be computed as time = game_ticks/60 for a game that runs
                        # at 60fps
    
  def __str__(self):
    hit_str =''
    for b in self.hit_boxes:
      hit_str += '\t' + str(b) + '\n' 
    
    col_str = ''
    for b in self.damage_boxes:
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
    """%(self.group_no,self.im_no,len(self.hit_boxes),hit_str,len(self.damage_boxes),col_str,self.game_ticks)
    return s
       
class AnimationInfo(object):  

  """
  Class that stores the animation elements and other relevant data associated with a "Animation Action" as define in a M.U.G.E.N Air file
  """
  
  DEFAULT_FPS = 60.0
    
  def __init__(self,name = ''):
    self.name = name
    self.id = 0
    self.loopstart = 0
    self.loop_mode = True
    self.scalex = 1
    self.scaley = 1
    self.framerate = 0          # average fps
    self.rigid_body_boxes = []  # boxes used to represent the rigid body that is subjected to the world physics'. It is the last box in the Clsn2Default list.
    self.auxiliary_boxes = []   # boxes used for especialized actions.  It's composed of the boxes in the Clsn2Default list except for the last
    self.action_boxes = []      # boxes used for responding to landmarks in the environment. It's composed of the boxes in the Clsn1Default list.
    self.animation_elements =[] # list of AnimationElement objects, should be the same size as the number of sprites lists.
    self.sprites_left = []      # list of objects of the Sprite class for the left animation
    self.sprites_right = []     # list of objects of the Sprite class for the right animation
    self.sprites_time = []      # list of time values (seconds) each frame is shown
    
  def __str__(self):
    hit_str = ''
    for b in self.action_boxes:
      hit_str+= '\t' + str(b) + '\n' 
      
    col_str = ''
    for b in self.rigid_body_boxes:
      col_str += '\t' + str(b) + '\n'
      
    elmt_str = ''
    for elmt in self.animation_elements:
      elmt_str += '\t' + str(elmt) + '\n'
    
    s = """
    Animation Action: %s
      id : %i
      framerate : %i
      loopstart : %i
      loop_mode : %s
      collision boxes : %i
      %s
      hit boxes: %i
      %s
      animation elements: 
        %s
    """%(self.name,
         self.id,
         self.framerate,
         self.loopstart,
         ('TRUE' if self.loop_mode else 'FALSE'),
         len(self.rigid_body_boxes),
         col_str,len(self.action_boxes),
         hit_str,
         elmt_str)
    
    return s
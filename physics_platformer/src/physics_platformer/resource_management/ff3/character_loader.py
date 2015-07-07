from physics_platformer.ff3 import FFELoader
from physics_platformer.ff3 import AIRLoader
import os
import logging
import re

class AnimationDetails(object):  
  
  def __init__(self):
    
    self.name = ''
    self.hit_boxes_ = []
    self.action_boxes_ = []
    self.images_ = []
    self.framerate_ = 0
    

class CharacterLoader(object):
  
  __EXTENSION__ = '.def'
  __ANIM_FILE_ENTRY__ = 'anim = (.+)'
  __SPRITE_DIR__ = 'sprites'
  __SPRITE_FILE__ = 'sprites.ffe'
  
  def __init__(self):
    """
    Loads Animation Actions from an AIR File created in Fighter Factory 3
    """
    
    self.name_ = ''
    self.displayname_ = ''
    self.dir_ = '' # parent directory
    self.filename_ = ''
    self.sprite_dir_ = CharacterLoader.__SPRITE_DIR__
    self.anim_file_ = '' # .air file
    self.sprite_file_ = CharacterLoader.__SPRITE_FILE__
    self.anims_dict_ = {}
    
    
  def load(self,filename):
    
    """
    bool load(string filename)
    Loads a character resources that were generated with the Fighter Factory 3 software. The .def file
    constains information about the location of the .air, .cns , .ssf, etc files that define the various
    resources that make up the character (At this point only the .air file is used.  It is assumed that
    there exists a 'sprites' directory inside the parent directory of the .def file that contains all of
    the sprites as well as the 'sprites.def' file.
    - Inputs
     filename: Path to a .def file
     - Outputs
      succeeded Boolean
    """
    # openning file
    if not ( os.path.exists(filename) and filename.endswith(CharacterLoader.__EXTENSION__)):
      logging.error("File %s is invalid"%(filename))
      return False
      
    dirname, junk = os.path.split(os.path.abspath(filename))
    self.dir_ = dirname
      
    f = open(filename,'r')
    lines = f.readlines()    
    logging.debug("File %s contains %i lines"%(filename,len(lines)))
    
    
    linecount = 0
    while linecount < len(lines):    
      line = lines[linecount]
      linecount+=1
    
      # finding .air file    
      anim_full_path = ''
      m = re.search(CharacterLoader.__ANIM_FILE_ENTRY__, line)
      if m is not None:
        self.anim_file_ = m.group(1)
        anim_full_path = os.path.join(self.dir_,self.anim_file_)
      else:
        continue
        
      air_loader = AIRLoader()
      if not air_loader.load(anim_full_path):
        logging.error('Air file failed to load')
        break
        
      break 
    
    
    
    
    
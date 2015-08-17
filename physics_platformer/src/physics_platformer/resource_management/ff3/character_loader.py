from physics_platformer.resource_management.ff3 import FFELoader
from physics_platformer.resource_management.ff3 import AIRLoader
from physics_platformer.resource_management.ff3 import CNSLoader
from physics_platformer.animation import AnimationActor
import os
import logging
import re

    

class CharacterLoader(object):
  
  __EXTENSION__ = '.def'
  __PLAYER_NAME_ENTRY__ = 'name\s+=\s+"(.+)"'
  __ANIM_FILE_ENTRY__ = 'anim\s+=\s+(.+)'
  __CNS_FILE_ENTRY__ = 'cns\s+=\s+(.+)'
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
    self.cns_file_ = '' # .cns file
    self.sprite_file_ = CharacterLoader.__SPRITE_FILE__
    self.anims_dict_ = {}
    self.animation_actors_ = []
    self.sprite_loader_ = None
    self.anim_loader_ = None
    self.cns_loader_ = None
  
  def getAnimations(self):
    return self.anims_dict_.values()
  
  def getAnimation(self,name):
    self.anims_dict_.get(name,None)
    
    
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
    success = True
    
    anim_file_path = ''
    ffe_file_name = ''
    cns_file_path = ''
    while linecount < len(lines):    
      line = lines[linecount]
      linecount+=1
      
      # finding player name
      m = re.search(CharacterLoader.__PLAYER_NAME_ENTRY__,line)
      if m is not None:
        self.name_ = m.group(1)
        continue
    
      # finding .air file    
      m = re.search(CharacterLoader.__ANIM_FILE_ENTRY__, line)
      if m is not None:
        
        self.anim_file_ = (m.group(1)).rstrip(' \t\n\r')
        anim_file_path = os.path.join(self.dir_,self.anim_file_)
        continue
      
      # finding .cns files
      m = re.search(CharacterLoader.__CNS_FILE_ENTRY__, line)
      if m is not None:
                
        self.cns_file_ = (m.group(1)).rstrip(' \t\n\r')
        cns_file_path = os.path.join(self.dir_,self.cns_file_)
        continue
      
    if anim_file_path and cns_file_path :
      success = True
    else:
      logging.error("Finished parsing %s file, no valid entries were found"%(filename))
      return False  
    
    logging.debug("Finished parsing %s file"%(filename))
    logging.debug("The following entries were found:")
    logging.debug("\tname    :\t%s"%(self.name_))
    logging.debug("\tair file:\t%s"%(self.anim_file_))
    logging.debug("\tcns file:\t%s"%(self.cns_file_))
    
    self.cns_loader_ = CNSLoader()
    if not self.cns_loader_.load(cns_file_path):
      logging.error("CNS file %s failed to load"%(cns_file_path))
      return False
       
    # loading air file        
    self.anim_loader_ = AIRLoader()
    if not self.anim_loader_.load(anim_file_path):
      logging.error("Air file %s failed to load"%(anim_file_path))
      return False
    
    # loading sprites from ffe file 
    ffe_file_name = os.path.join(self.dir_,CharacterLoader.__SPRITE_DIR__,CharacterLoader.__SPRITE_FILE__)
    self.sprite_loader_ = FFELoader()
    if not self.sprite_loader_.load(ffe_file_name,self.anim_loader_.groups):
      logging.error("FFE file %s failed to load"%(ffe_file_name))
      return False
    self.__loadSpritesIntoAnimations__()
      
    # creating animations dictionary
    for anim in self.anim_loader_.animations:
      if self.anims_dict_.has_key(anim.name):
        logging.warn("Multiple animations with the name %s have been found, only the last one will be stored")        
      self.anims_dict_[anim.name] = anim
      
    self.__createAnimationActors__()
        
    self.cns_loader_ = None
    self.sprite_loader_ = None
    self.anim_loader_ = None
    
    return success
  
  def __loadSpritesIntoAnimations__(self):
    
    for anim in self.anim_loader_.animations:
      for elemt in anim.animation_elements:
        
        # saving right sprite
        sprt_right = self.sprite_loader_.getSprite(elemt.group_no,elemt.im_no)
        sprt_right.hit_boxes = elemt.hit_boxes
        sprt_right.collision_boxes = elemt.collision_boxes        
        
        # saving left sprite
        sprt_left = self.sprite_loader_.getSprite(elemt.group_no,elemt.im_no,False) 
        for hb in elemt.hit_boxes:
          sprt_left.hit_boxes.append(hb.flipX())
        
        for cb in elemt.collision_boxes:
          sprt_left.collision_boxes.append(cb.flipX())
        
        
        anim.sprites_right.append(sprt_right)
        anim.sprites_left.append(sprt_left)
        
  def __createAnimationActors__(self):
    
    self.animation_actors_ = []
    character_info = self.cns_loader_.getCharacterInfo()
    for anim in self.anim_loader_.animations:
      actor = AnimationActor(anim.name)
      actor.loadAnimation(anim)
      actor.setScale(character_info.scale)
      self.animation_actors_.append(actor)
        
        
    
    
    
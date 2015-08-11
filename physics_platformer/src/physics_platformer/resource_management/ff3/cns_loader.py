from physics_platformer.game_object import CharacterInfo
from panda3d.core import Vec3
import os
import re

class CNSLoader(object):
  
  __EXTENSION__ = '.cns'
  
  
  class DataTokens(object):
    __LIFE__ = 'life\s+=\s+(\d+)'
    __POWER__ = 'power\s+=\s+(\d+)'
    __DEFENSE__ = 'defence\s+=\s+(\d+)'
    __ATTACK__ = 'attack\s+=\s+(\d+)'
    
  class SizeTokens(object):
    __XSCALE__= 'xscale\s+=\s+(\d+\.?\d*)'
    __YSCALE__= 'yscale\s+=\s+(\d+\.?\d*)'
    
  class VelocityTokens(object):
    __WALK__ = 'walk\.fwd\s+=\s+(\d+)'
    __RUN__= 'run\.fwd\s+=\s+(\d+)'
    __JUMP_UP__ = '^jump\.neu\s+=\s+\d+,([-+]?\d)'
    __JUMP_FORWARD__ = '^jump\.fwd\s+=\s+(\d+)'
    
  class MovementTokens(object):    
    __AIR_JUMPS__ = 'airjump.num\s+=\s+(\d+)'
    
    
  
  def __init__(self):
    """
    Loads general player data from a .cns file created in Fighter Factory 3
    """
    self.char_info_ = CharacterInfo()
    
  def getCharacterInfo(self):
    return self.char_info_
  
  def load(self,filename):
    
        # openning file
    if not ( os.path.exists(filename) and filename.endswith(CNSLoader.__EXTENSION__)):
      logging.error("File %s is invalid"%(filename))
      return False
    
    f = open(filename,'r')
    lines = f.readlines()

    self.char_info_ = CharacterInfo()
    linecount = 0
    lines_read = 0
    while linecount < len(lines):   
      
      line = lines[linecount]      
      linecount+=1     
      
      if self.__readDataEntries__(line):   
        lines_read += 1     
        continue
      
      if self.__readSizeEntries__(line):
        lines_read += 1 
        continue
      
      if self.__readVelocityEntries__(line):
        lines_read += 1 
        continue
      
      if self.__readMovementsEntries__(line):
        lines_read += 1 
        continue
        
    
    if lines_read == 0:
      return False
    
    return True
      
      
      
  def __readDataEntries__(self,line):   
    
    
    m = re.search(CNSLoader.DataTokens.__ATTACK__,line)
    if m is not None:
      self.char_info_.attack = int(m.group(1))
      return True
    
    m = re.search(CNSLoader.DataTokens.__LIFE__,line)
    if m is not None:
      self.char_info_.life = int(m.group(1))
      return True
    
    m = re.search(CNSLoader.DataTokens.__POWER__,line)
    if m is not None:
      self.char_info_.power = int(m.group(1))
      return True
  
    m = re.search(CNSLoader.DataTokens.__DEFENSE__,line)
    if m is not None:
      self.char_info_.defense = int(m.group(1))
      return True
    
    return False
  
  def __readSizeEntries__(self,line):
    
    x = self.char_info_.scale.getX()
    y = self.char_info_.scale.getY()  
    z = self.char_info_.scale.getZ()   
    m = re.search(CNSLoader.SizeTokens.__XSCALE__,line)
    if m is not None:
      x= float(m.group(1))
      self.char_info_.scale = Vec3(x,y,z)
      return True
    
    m = re.search(CNSLoader.SizeTokens.__YSCALE__,line)
    if m is not None:
      z= float(m.group(1))
      self.char_info_.scale = Vec3(x,y,z)
      return True
        
    return False
  
  def __readVelocityEntries__(self,line):
    
    m = re.search(CNSLoader.VelocityTokens.__JUMP_FORWARD__,line)
    if m is not None:
      self.char_info_.jump_forward = float(m.group(1))
      return True
    
    m = re.search(CNSLoader.VelocityTokens.__JUMP_UP__,line)
    if m is not None:
      self.char_info_.jump_force = float(m.group(1))
      return True
    
    m = re.search(CNSLoader.VelocityTokens.__WALK__,line)
    if m is not None:
      self.char_info_.walk_speed = float(m.group(1))
      return True
    
    m = re.search(CNSLoader.VelocityTokens.__RUN__,line)
    if m is not None:
      self.char_info_.run_speed = float(m.group(1))
      return True
    
    return False
  
  def __readMovementsEntries__(self,line):
    
    m = re.search(CNSLoader.MovementTokens.__AIR_JUMPS__,line)
    if m is not None:
      self.char_info_.air_jumps = int(m.group(1))
      return True
    
    return False
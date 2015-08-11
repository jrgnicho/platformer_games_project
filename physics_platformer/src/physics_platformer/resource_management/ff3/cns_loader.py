from physics_platformer.game_object import CharacterInfo

class CNSLoader(object):
  
  __EXTENSION__ = '.cns'
  
  
  class DataTokens(object):
    __LIFE__ = 'life =  (\d+)'
    __POWER__ = 'power = (\d+)'
    __DEFENSE__ = 'defense = (\d+)'
    __ATTACK__ = 'attack = (\d+)'
    
  class SizeTokens(object):
    __XSCALE__= 'xscale = (\d+\.?\d*)'
    __YSCALE__= 'yscale = (\d+\.?\d*)'
    
  class VelocityTokens(object):
    __WALK__ = 'walk.fwd = (\d+)'
    __RUN__= 'run.fwd = (\d+)'
    __JUMP_UP__ = 'jump.neu = \d+,([-+]?\d)'
    __JUMP_FORWARD__ = 'jump.fwd = (\d)'
    
  class MovementTokens(object):    
    __AIR_JUMPS__ = 'airjump.num = \d+'
    
    
  
  def __init__(self):
    """
    Loads general player data from a .cns file created in Fighter Factory 3
    """
    pass
  
  def load(self,filename):
    
        # openning file
    if not ( os.path.exists(filename) and filename.endswith(CNSLoader.__EXTENSION__)):
      logging.error("File %s is invalid"%(filename))
      return False
    
    f = open(filename,'r')
    lines = f.readlines()
    
    self.animations_ = []    
    linecount = 0    
    anim_action = None
    anim_elmt = None
    
    while linecount < len(lines):   
      
      line = lines[linecount]      
      linecount+=1     
      
      m = re.search(AIRLoader.__ANIMATION_NAME__,line)
      if m is not None: # new animation found
        
        pass
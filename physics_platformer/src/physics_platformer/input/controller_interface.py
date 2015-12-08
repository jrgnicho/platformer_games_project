from physics_platformer.input import JoystickButtons
from physics_platformer.input import Move


class ControllerInterface(object):
    """
        Interface class for input devices
    """
    
    def __init__(self):
      self.button_press_moves_ = []
      self.button_release_moves_ = []
        
    def setMoves(self, move_list, button_press=True):
      '''
      ControllerInterface.setMoves()
      '''
      if button_press:
        self.button_press_moves_ = sorted(move_list, key=lambda move : len(move) + int( not move.is_submove), reverse=True)
      else:
        self.button_release_moves_ = sorted(move_list, key=lambda move : len(move) + int( not move.is_submove), reverse=True)
        
    def addMove(self, move, button_press=True):
      if button_press:
        self.button_press_moves_.append(move)        
        self.setMoves(self.button_press_moves_, button_press) 
      else:
        self.button_release_moves_.append(move)        
        self.setMoves(self.button_release_moves_, button_press)         
       
      
      print "Added new %s move to ControllerInterface" % (move.name)  
        
    def reset(self):
      pass
 
    def update(self, dt=0):
      """
          This method will be called on each game update and it is expected to check for move matches
      """ 
      pass    
   

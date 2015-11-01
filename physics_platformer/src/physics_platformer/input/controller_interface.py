from physics_platformer.input import JoystickButtons
from physics_platformer.input import Move


class ControllerInterface(object):
    """
        Interface class for input devices
    """
    
    def __init__(self):
        self.moves_ = []
        
    def set_moves(self,move_list):
        self.moves_ = sorted(move_list,key = lambda move : len(move),reverse = True)
        
    def add_move(self,move):
        self.moves_.append(move)
        self.set_moves(self.moves_)  
        
        print "Added new %s move to ControllerInterface"%(move.name)  
        
    def reset(self):
      pass
 
    def update(self,dt = 0):
        """
            This method will be called on each game update and it is expected to check for move matches
        """ 
        pass    
   
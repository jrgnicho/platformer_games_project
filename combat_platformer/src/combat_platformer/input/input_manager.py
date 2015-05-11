from combat_platformer.input import JoystickButtons
from combat_platformer.input import Move
from pygame.time import Clock
import sys


class InputManager(object):
    """
        Interface class for input devices
    """
    
    def __init__(self):
        self.__moves__ = []
        
    def set_moves(self,move_list):
        self.__moves__ = sorted(move_list,key = lambda move : len(move),reverse = True)
        
    def add_move(self,move):
        self.__moves__.append(move)
        self.set_moves(self.__moves__)  
        
        print "Added new %s move to InputManager"%(move.name)  
 
    def update(self,dt = 0):
        """
            This method will be called on each game update and it is expected to check for move matches
        """ 
        pass    
   
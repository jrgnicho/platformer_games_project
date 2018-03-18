import sys, os
from pygame.joystick import Joystick
from platformer_core.input import JoystickButtons

class JoystickState(object):
    
    def __init__(self,joystick):
        
        self.axes = [0.0]*joystick.get_numaxes()
        self.buttons = [False]*joystick.get_numbuttons()
        self.hats =[(0,0)]*joystick.get_numhats()   
        
    def capture(self,joystick):
        
        
        # capturing axes
        for i in range(joystick.get_numaxes()):
            self.axes[i] = joystick.get_axis(i)
        #endfor
        
        for i in range(joystick.get_numbuttons()):
            self.buttons[i] = joystick.get_button(i)
        #endfor
        
        for i in range(joystick.get_numhats()):
            self.hats[i] = joystick.get_hat(i)
        #endfor
                
    
    def isAxisDown(self,axis,r):
        """
        JoystickState::isAxisDown(axis,range)
            Checks if the axis is at a value within the range
            Inputs:
            - axis: Integer corresponding to the axis index in the joystick
            - range: Two element tuple containing the (min,max) values where the axis is considered to be pressed
            Output:
            - Bool: True | False boolean 
        """
        if len(self.axes) > axis:
            return (self.axes[axis] >= r[0] and self.axes[axis] <= r[1])
        else:
            return False
        #endif
        
    def isButtonDown(self,button):
        """
        Inputs:
            - button : Button index integer
        Output:
            - Bool : True | False
        """
        
        if len(self.buttons) > button:
            return self.buttons[button]
        else:
            return False
        #endif
        
    def isHatDown(self,hat,pos):
        """
        Inputs:
            - hat: Hat index integer
            - pos: Tuple (x,y) with the position values
        Output
            - Bool : True | False            
        """
        
        if len(self.hats) > hat:
            return self.hats[hat] == pos
        else:
            return False
        #endif
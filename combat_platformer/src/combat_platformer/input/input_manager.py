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
        self.__moves__ = sorted(move_list,key = lambda move : len(move),True)
        
    def add_move(self,move):
        self.__moves__.append(move)
        self.set_moves(self.__moves__)    
 
    def update(self,dt = 0):
        """
            This method will be called on each game update and it is expected to check for move matches
        """ 
        pass    

    
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
        
    
    def is_axis_down(self,axis,r):
        """
        JoystickState::is_axis_down(axis,range)
            Checks if the axis is at a value within the range
            Inputs:
            - axis: Integer corresponding to the axis index in the joystick
            - range: Two element tuple containing the (min,max) values where the axis is considered to be pressed
            Output:
            - Bool: True | False boolean 
        """
        if len(self.axes) > axis:
            return (self.axes[axis] >= r(0) and self.axes[axis] <= r(1))
        else:
            return False
        #endif
        
    def is_button_down(self,button):
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
        
    def is_hat_down(self,hat,pos):
        """
        Inputs:
            - hat: Hat index integer
            - vals: Tuple (x,y) with the position values
        Output
            - Bool : True | False            
        """
        
        if len(self.hats) > hat:
            return self.hats[hat] == pos
        else:
            return False
        #endif
        
class JoystickAxes(object):
    
    def __init__(self,x_axis = 0,y_axis = 1,xrange = (0.5,1.0) ,yrange = (0.5,1.0)):      
        
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.xrange = xrange
        self.yrange = yrange
        
    def get_direction(self,js):
        
        """
        JoystickAxes.get_direction(joystick_state)
            Gets the current joystick direction
            Inputs:
            - joystick_state: Joystick state object
            Output:
            - Button: Bitmask containing the button direction
        """
        
        direction = JoystickButtons.NONE
        
        # check x direction
        if js.is_axis_down(self.x_axis,(self.xrange[0],self.xrange[1])):    
            direction = direction | JoystickButtons.DPAD_RIGHT
        
        if js.is_axis_down(self.x_axis,(-self.xrange[1],-self.xrange[0])): 
            direction = direction | JoystickButtons.DPAD_LEFT
            
        if js.is_axis_down(self.y_axis,(self.yrange[0],self.yrange[1])): 
            direction = direction | JoystickButtons.DPAD_UP
            
        if js.is_axis_down(self.y_axis,(-self.yrange[1],-self.yrange[0])): 
            direction = direction | JoystickButtons.DPAD_DOWN
            
        return direction
        
class JoystickManager(InputManager):
    
    
    # saved to suppress unwanted debug output from SDL
    __STDOUT__ = sys.stdout
    
    def __init__(self):
        InputManager.__init__(self,button_map,joystick_axes,buffer_timeout)
        
        self.__buffer_timeout__ = buffer_timeout # buffer is cleared when this value is exceeded
        self.__button_map__ = button_map # dictionary containing the mapping of the device button index (key)
                                         # and the button mask (value)
        self.__joystick_axes__ = joystick_axes # Joystick axes object
        
                                         
    def __check_state__(self):
        pass
    
    # for supressing SDL output to stdout
    def suppress_stdout(supress):
        with open(os.devnull, "w") as devnull:
            sys.stdout = devnull if supress else JoystickManager.__STDOUT__
            try:  
                yield
            finally:
                sys.stdout = JoystickManager.__STDOUT__
    
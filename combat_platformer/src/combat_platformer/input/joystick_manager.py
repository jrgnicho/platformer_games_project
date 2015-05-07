from combat_platformer.input import InputManager
from combat_platformer.input import JoystickButtons
from combat_platformer.input import JoystickState

        
class JoystickManager(InputManager):
    
    
    # saved to suppress unwanted debug output from SDL
    __STDOUT__ = sys.stdout
    
    class JoystickAxes(object):
        """ JoystickAxes
                Utility class for detecting the direction of the joystick from a 
                combat_platformer.input.JoystickState object
        """
    
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
    
    
    
    """
    ## JoystickManager(button_map, joystick_axes, buffer_timeout)
    #  @param button_map     A dictionary containing the mapping between the indices for buttons as defined by the pygame.joystick.Joystick
    #                        interface (keys) and the constants defined in the combat_platformer.input.JoystickButtons class (values).
    #  @param joystick_axes  A combat_platformer.input.JoystickAxes object for detection the direction of the D-pad
    #  @param buffer_timeout A float in seconds.  The button buffer is cleared when this value is exceeded 
    """  
    def __init__(self,button_map,joystick_axes,buffer_timeout):

        
        InputManager.__init__(self)
        
        self.__buffer_timeout__ = buffer_timeout    # Buffer is cleared when this value is exceeded.
        self.__button_map__ = button_map            # Dictionary containing the mapping of the device button index (key) in the 
                                                    # pygame.joystick.Joystick interface and the constants defined in the 
                                                    # combat_platformer.input.JoystickButtons class
                                                    # and the button mask (value)
        self.__joystick_axes__ = joystick_axes      # Joystick axes object for detecting the direction of the D-pad
        
        # Support members
        self.__button_buffer__ = []
        self.__time_elapsed__ = 0.0
        
        # Initializing Joystick support
        
        self.__joystick_state__ = None   
        self.__joystick__ = None     
        pygame.joystick.init()
        
        if pygame.joystick.get_count() > 0 :
            print "Enabling Joystick 0"
            self.__joystick__ = pygame.joystick.Joystick(0)
            
            # Instantiating a JoystickState 
            self.__joystick_state__ = JoystickState(self.__joystick__)
        else:
            print "ERROR: Joystick was not found"
        
                                         
    def update(self,dt = 0):
        
        InputManager.update(self,dt)
        
        # Update internal time elapsed and clear buffer if timeout exceeded
        self.__time_elapsed__ = self.__time_elapsed__ + dt
        if self.__time_elapsed__ > self.__buffer_timeout__:
            self.__button_buffer__ = []
        
        if self.__joystick__ == None:
            print "ERROR: No joystick found"
            return 
                        
        # Capturing Joystick Buttons
        self.__joystick_state__.capture(self.__joystick__)
        
        buttons = self.__joystick_axes__.get_direction(self.__joystick_state__)
        button_count = self.__joystick__.get_numbuttons()
        for i in range(0,button_count):
            if self.__joystick_state__.is_button_down(i):
                
                # Combining button presses
                buttons = buttons | self.__button_map__[i]
                
        # Saving buttons pressed into buffer
        self.__button_buffer__.append(buttons)
        
        # Checking for activated moves
        move_count = len(self.__moves__)
        for i in range(0,move_count):
            if self.__moves__[i].match(self.__button_buffer__):
                self.__moves__[i].execute()
                
                # Clear buffer if move is not part of another move
                if not self.__moves__[i].is_submove:
                    self.__button_buffer__ = []
        
        
        
    
    # for supressing SDL output to stdout
    def suppress_stdout(supress):
        with open(os.devnull, "w") as devnull:
            sys.stdout = devnull if supress else JoystickManager.__STDOUT__
            try:  
                yield
            finally:
                sys.stdout = JoystickManager.__STDOUT__
    
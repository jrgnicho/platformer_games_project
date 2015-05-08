from contextlib import contextmanager
import sys, os, cStringIO
import pygame.joystick
from combat_platformer.input import InputManager
from combat_platformer.input import JoystickButtons
from combat_platformer.input import JoystickState

        
class JoystickManager(InputManager):
    
    MAX_BUFFER_SIZE = 30   

    
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
                direction = direction | JoystickButtons.DPAD_DOWN
                
            if js.is_axis_down(self.y_axis,(-self.yrange[1],-self.yrange[0])): 
                direction = direction | JoystickButtons.DPAD_UP
                
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
        self.__time_elapsed__ = 0
        
        # Initializing joystick support members        
        self.__joystick_state__ = None   
        self.__joystick__ = None    
        
        if pygame.joystick.get_count() > 0 :
            print "Enabling Joystick 0"
            self.__joystick__ = pygame.joystick.Joystick(0)
            self.__joystick__.init()
            
            # Instantiating a JoystickState 
            self.__joystick_state__ = JoystickState(self.__joystick__)
        else:
            print "ERROR: Joystick was not found"
        
                                         
    def update(self,dt = 0):
        
        #print "JoystickManager Update Started"
        
        InputManager.update(self,dt)
        
        # Update internal time elapsed and clear buffer if timeout exceeded
        self.__time_elapsed__ = self.__time_elapsed__ + dt
        if self.__time_elapsed__ > self.__buffer_timeout__:
            
            #print "Time Elapsed %i exceeded Buffer Timeout %i"%(self.__time_elapsed__,self.__buffer_timeout__)
            self.__time_elapsed__ = 0
            self.__button_buffer__ = []
        
        if self.__joystick__ == None:
            print "ERROR: No joystick found"
            return   
   
        # Capturing Joystick Buttons
        #with self.suppress_stdout():
        self.__joystick_state__.capture(self.__joystick__)

                
        # Combining pressed buttons
        buttons = self.__joystick_axes__.get_direction(self.__joystick_state__)                 
        button_count = self.__joystick__.get_numbuttons()
        for i in range(0,button_count):
            if self.__joystick_state__.is_button_down(i):
                
                # Combining button presses
                buttons = buttons | self.__button_map__[i]
                
        # Saving buttons pressed into buffer        
        if (len(self.__button_buffer__) == 0):            
            self.__button_buffer__.append(buttons)
        else:
            if buttons != self.__button_buffer__[-1]:
                self.__button_buffer__.append(buttons)
        #print "Button Buffer has %i entries"%(len(self.__button_buffer__))
        
        
        
        # Keeping buffer size to max allowed
        if len(self.__button_buffer__) > JoystickManager.MAX_BUFFER_SIZE:
            del self.__button_buffer__[0]
        
        # Checking for activated moves
        move_count = len(self.__moves__)
        for i in range(0,move_count):
            
            if not self.__moves__[i].is_submove:  
                     
                if self.__moves__[i].match(self.__button_buffer__):
                    self.__moves__[i].execute()
                    self.__button_buffer__ = []      
                    break   

            else:                 
                        
                num_buttons = len(self.__moves__[i])
                if self.__moves__[i].match(self.__button_buffer__[-num_buttons:]):
                    self.__moves__[i].execute()

        
        
        #print "JoystickManager Update Completed"
            
    @contextmanager       
    def suppress_stdout(self):
        '''Prevent print to stdout, but if there was an error then catch it and
        print the output before raising the error.'''
    
        saved_stdout = sys.stdout
        sys.stdout = cStringIO.StringIO()
        try:
            yield
        except Exception:
            saved_output = sys.stdout
            sys.stdout = saved_stdout
            print saved_output.getvalue()
            raise
        sys.stdout = saved_stdout
            

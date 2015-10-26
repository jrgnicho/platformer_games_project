from contextlib import contextmanager
import sys, os, cStringIO
import pygame.joystick
from physics_platformer.input import InputManager
from physics_platformer.input import JoystickButtons
from physics_platformer.input import JoystickState

        
class JoystickManager(InputManager):
    
    MAX_BUFFER_SIZE = 30   

    
    class JoystickAxes(object):
        """ JoystickAxes
                Utility class for detecting the direction of the joystick from a 
                physics_platformer.input.JoystickState object
        """
    
        def __init__(self,x_axis = 0,y_axis = 1,xrange = (0.5,1.0) ,yrange = (0.5,1.0)):      
            
            self.x_axis_ = x_axis
            self.y_axis_ = y_axis
            self.xrange_ = xrange
            self.yrange_ = yrange
            
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
            if js.is_axis_down(self.x_axis_,(self.xrange_[0],self.xrange_[1])):    
                direction = direction | JoystickButtons.DPAD_RIGHT
            
            if js.is_axis_down(self.x_axis_,(-self.xrange_[1],-self.xrange_[0])): 
                direction = direction | JoystickButtons.DPAD_LEFT
                
            if js.is_axis_down(self.y_axis_,(self.yrange_[0],self.yrange_[1])): 
                direction = direction | JoystickButtons.DPAD_DOWN
                
            if js.is_axis_down(self.y_axis_,(-self.yrange_[1],-self.yrange_[0])): 
                direction = direction | JoystickButtons.DPAD_UP
                
            return direction
    
    
    
    """
    ## JoystickManager(button_map, joystick_axes, buffer_timeout)
    #  @param button_map     A dictionary containing the mapping between the indices for buttons as defined by the pygame.joystick.Joystick
    #                        interface (keys) and the constants defined in the physics_platformer.input.JoystickButtons class (values).
    #  @param joystick_axes  A physics_platformer.input.JoystickAxes object for detection the direction of the D-pad
    #  @param buffer_timeout A float in seconds.  The button buffer is cleared when this value is exceeded 
    """  
    def __init__(self,button_map,joystick_axes,buffer_timeout):

        
        InputManager.__init__(self)
        
        self.buffer_timeout_ = buffer_timeout    # Buffer is cleared when this value is exceeded.
        self.button_map_ = button_map            # Dictionary containing the mapping of the device button index (key) in the 
                                                    # pygame.joystick.Joystick interface and the constants defined in the 
                                                    # physics_platformer.input.JoystickButtons class
                                                    # and the button mask (value)
        self.joystick_axes_ = joystick_axes      # Joystick axes object for detecting the direction of the D-pad
        
        # Support members
        self.button_buffer_ = []
        self.time_elapsed_ = 0
        
        # Initializing joystick support members        
        self.joystick_state_ = None   
        self.joystick_ = None    
        
        if pygame.joystick.get_count() > 0 :
            print "Enabling Joystick 0"
            self.joystick_ = pygame.joystick.Joystick(0)
            self.joystick_.init()
            
            # Instantiating a JoystickState 
            self.joystick_state_ = JoystickState(self.joystick_)
        else:
            print "ERROR: Joystick was not found"
            
    def reset(self):
      
      self.time_elapsed_ = 0
      self.button_buffer_ = []        
                                         
    def update(self,dt = 0):
        
        #print "JoystickManager Update Started"
        
        InputManager.update(self,dt)
        
        # Update internal time elapsed and clear buffer if timeout exceeded
        self.time_elapsed_ = self.time_elapsed_ + dt
        if self.time_elapsed_ > self.buffer_timeout_:
            
            self.time_elapsed_ = 0
            self.button_buffer_ = []
        
        if self.joystick_ == None:
            print "ERROR: No joystick found"
            return   
   
        # Capturing Joystick Buttons
        self.joystick_state_.capture(self.joystick_)
                
        # Combining pressed buttons
        buttons = self.joystick_axes_.get_direction(self.joystick_state_)                 
        button_count = self.joystick_.get_numbuttons()
        for i in range(0,button_count):
            if self.joystick_state_.is_button_down(i):
                
                # Combining button presses
                buttons = buttons | self.button_map_[i]
                
        # Saving buttons pressed into buffer        
        if (len(self.button_buffer_) == 0):            
            self.button_buffer_.append(buttons)
        else:
            if buttons != self.button_buffer_[-1]:
                self.button_buffer_.append(buttons)
        
        
        
        # Keeping buffer size to max allowed
        if len(self.button_buffer_) > JoystickManager.MAX_BUFFER_SIZE:
            del self.button_buffer_[0]
        
        # Checking for activated moves
        move_count = len(self.moves_)
        for i in range(0,move_count):
            
            if not self.moves_[i].is_submove:  
                     
                if self.moves_[i].match(self.button_buffer_):
                    self.moves_[i].execute()
                    self.button_buffer_ = []      
                    break   
            else:                 
                        
                num_buttons = len(self.moves_[i])
                if self.moves_[i].match(self.button_buffer_[-num_buttons:]):
                    self.moves_[i].execute()

        
        
            
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
            

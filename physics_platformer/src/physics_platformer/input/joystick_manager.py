
from physics_platformer.input import InputManager
from physics_platformer.input import JoystickButtons
from physics_platformer.input import JoystickState
import pygame.joystick
import logging


        
class JoystickManager(InputManager):
    
    __DEFAULT_BUFFER_TIMEOUT__ = 2 # 2 seconds
    __MAX_BUFFER_SIZE__ = 30   
    
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
    def __init__(self,button_map,joystick_axes,buffer_timeout = __DEFAULT_BUFFER_TIMEOUT__):

        
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
            logging.info("Enabling Joystick 0")
            self.joystick_ = pygame.joystick.Joystick(0)
            self.joystick_.init()
            
            # Instantiating a JoystickState 
            self.joystick_state_ = JoystickState(self.joystick_)
        else:
            logging.error( "ERROR: Joystick was not found")
            
    def reset(self):
      
      self.time_elapsed_ = 0
      self.button_buffer_ = []      
        
                                         
    def update(self,dt = 0):
        
      
      InputManager.update(self,dt)
      
      # Update internal time elapsed and clear buffer if timeout exceeded
      self.time_elapsed_ = self.time_elapsed_ + dt
      if self.time_elapsed_ > self.buffer_timeout_:            
          self.reset()
      
      if self.joystick_ == None:
          logging.error( "ERROR: No joystick found")
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
      if len(self.button_buffer_) > JoystickManager.__MAX_BUFFER_SIZE__:
        del self.button_buffer_[0]
          
          
      # checking button combinations for matches
      matched_moves = self.findMatchingMoves(self.button_buffer_)
      for move in matched_moves:
        move.execute()
        if not move.is_submove:
          self.reset() # clear buffer
          break     


    def reset(self): 
      
      self.time_elapsed_ = 0
      self.button_buffer_ = [] 
    
    def findMatchingMoves(self,button_sequence):
      matched_moves = []
      for move in self.moves_:
        
        if move.match(button_sequence):
          matched_moves.append(move)
          if not move.is_submove:     
            break
      
      
      return matched_moves       

            

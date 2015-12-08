
from physics_platformer.input import ControllerInterface
from physics_platformer.input import JoystickButtons
from physics_platformer.input import JoystickState
import pygame.joystick
import logging


        
class JoystickController(ControllerInterface):
    
  DEFAULT_BUFFER_TIMEOUT = 0.2 #  seconds
  DEFAULT_MERGE_TIME = 0.1 # seconds 
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
          
      def getDirection(self,js):
          
          """
          JoystickAxes.getDirection(joystick_state)
              Gets the current joystick direction
              Inputs:
              - joystick_state: Joystick state object
              Output:
              - Button: Bitmask containing the button direction
          """
          
          direction = JoystickButtons.NONE
          
          if js.isAxisDown(self.x_axis_,(self.xrange_[0],self.xrange_[1])):    
              direction = JoystickButtons.DPAD_RIGHT
          
          if js.isAxisDown(self.x_axis_,(-self.xrange_[1],-self.xrange_[0])): 
              direction = JoystickButtons.DPAD_LEFT
              
          if js.isAxisDown(self.y_axis_,(self.yrange_[0],self.yrange_[1])): 
            direction = JoystickButtons.DPAD_DOWN
              
            if js.isAxisDown(self.x_axis_,(self.xrange_[0],self.xrange_[1])):    
                direction = JoystickButtons.DPAD_DOWNRIGHT
            
            if js.isAxisDown(self.x_axis_,(-self.xrange_[1],-self.xrange_[0])): 
                direction = JoystickButtons.DPAD_DOWNLEFT                
              
          if js.isAxisDown(self.y_axis_,(-self.yrange_[1],-self.yrange_[0])): 
            direction = JoystickButtons.DPAD_UP
            if js.isAxisDown(self.x_axis_,(self.xrange_[0],self.xrange_[1])):    
                direction = JoystickButtons.DPAD_UPRIGHT
            
            if js.isAxisDown(self.x_axis_,(-self.xrange_[1],-self.xrange_[0])): 
                direction = JoystickButtons.DPAD_UPLEFT
              
          return direction
  
  
  
  """
  ## JoystickController(dict<int,JoystickButton> button_map, pyagame.joystick.Joystick joystick_obj, JoystickAxes joystick_axes, buffer_timeout)
  #  @param button_map     A dictionary containing the mapping between the indices for buttons as defined by the pygame.joystick.Joystick
  #                        interface (keys) and the constants defined in the physics_platformer.input.JoystickButtons class (values).
  #  @param joystick_obj  The joystick interface.  Make sure that the pygame.joystick.init() method has been invoked
  #  @param joystick_axes  A physics_platformer.input.JoystickAxes object for detection the direction of the D-pad
  #  @param buffer_timeout A float in seconds.  The button buffer is cleared when this value is exceeded 
  """  
  def __init__(self,button_map,joystick_obj,joystick_axes,buffer_timeout = DEFAULT_BUFFER_TIMEOUT,merge_time = DEFAULT_MERGE_TIME):

      
      ControllerInterface.__init__(self)
      
      self.buffer_timeout_ = buffer_timeout    # Buffer is cleared when this value is exceeded.
      self.button_map_ = button_map            # Dictionary containing the mapping of the device button index (key) in the 
                                                  # pygame.joystick.Joystick interface and the constants defined in the 
                                                  # physics_platformer.input.JoystickButtons class
                                                  # and the button mask (value)
      self.joystick_axes_ = joystick_axes      # Joystick axes object for detecting the direction of the D-pad
      self.one_shot_mode_ = True
      
      # Support members
      self.button_press_buffer_ = []
      self.buffer_time_elapsed_ = 0
      self.merge_time_ = merge_time
      self.buffer_timeout_ = buffer_timeout
      self.button_release_buffer_ = []
      self.merge_time_elapsed_ = 0
  
      # history
      self.previous_buttons_down_ = JoystickButtons.NONE
      self.previous_directions_down_ = JoystickButtons.NONE
      self.buttons_down_ = JoystickButtons.NONE
      
      # Initializing joystick support members        
      self.joystick_state_ = None   
      self.joystick_ = joystick_obj   
      
      if not self.joystick_.get_init():
        self.joystick_.init()
        
      self.joystick_state_ = JoystickState(self.joystick_)
          
  def reset(self):    
    self.buffer_time_elapsed_ = 0
    self.button_press_buffer_ = []     
                                       
  def update(self,dt): 
    
    ControllerInterface.update(self,dt)
    
    if self.joystick_ == None:
        logging.error( "ERROR: No joystick found")
        return   

    # Capturing Joystick Buttons
    self.joystick_state_.capture(self.joystick_)
            
    # getting directions
    direction = self.joystick_axes_.getDirection(self.joystick_state_)  
     
    # combining button presses          
    button_count = self.joystick_.get_numbuttons()
    for i in range(0,button_count):
      if self.joystick_state_.isButtonDown(i):
          
        # Combining button presses
        self.buttons_down_ = self.buttons_down_ | self.button_map_[i]
          
    # buffering button presses
    buttons_pressed = JoystickButtons.NONE
    buttons_released = JoystickButtons.NONE
    
    
    # finding directions pressed
    buttons_pressed = direction & ~self.previous_directions_down_  if self.one_shot_mode_ else direction   

    # finding directions released
    buttons_released = ~direction & self.previous_directions_down_
    
    # storing last direction presses
    self.previous_directions_down_ = direction
    
    # merging directions with buttons pressed
    self.merge_time_elapsed_+=dt    
    if self.merge_time_elapsed_ > self.merge_time_:
      self.merge_time_elapsed_ = 0      
            
      # finding buttons pressed
      buttons_pressed =  buttons_pressed | (self.buttons_down_ & ~self.previous_buttons_down_  if self.one_shot_mode_ else self.buttons_down_)          
  
      # finding released buttons
      buttons_released = buttons_released | (~self.buttons_down_ & self.previous_buttons_down_)
      
      # storing last button presses
      self.previous_buttons_down_ = self.buttons_down_ 
      self.buttons_down_ = JoystickButtons.NONE
      
    
    # Saving and executing pressed moves    
    if buttons_pressed != JoystickButtons.NONE:
      self.button_press_buffer_ = self.storeIntoBuffer(self.button_press_buffer_, buttons_pressed)
      
      # checking button combinations for button press matches
      matched_moves = self.findMatchingMoves(self.button_press_moves_,self.button_press_buffer_)
      for move in matched_moves:
        move.execute()
        if not move.is_submove:
          self.reset() # clear buffer
          break  
      
    
    # Saving and executing released moves  
    if buttons_released != JoystickButtons.NONE:  
      self.button_release_buffer_ = self.storeIntoBuffer(self.button_release_buffer_, buttons_released)
        
      # checking button combinations for button release matches
      matched_moves = self.findMatchingMoves(self.button_release_moves_,self.button_release_buffer_)
      for move in matched_moves:
        move.execute()
        if not move.is_submove:
          self.button_release_buffer_ = []
          break
        
    # Update internal time elapsed and clear buffer when timeout is exceeded
    self.buffer_time_elapsed_ = self.buffer_time_elapsed_ + dt if buttons_pressed == JoystickButtons.NONE else 0
    if self.buffer_time_elapsed_ > self.buffer_timeout_:  
      self.reset()    

 
  def storeIntoBuffer(self, button_buffer,buttons):
    
    # Saving buttons into buffer      
    if (len(button_buffer) == 0):            
      button_buffer.append(buttons)
    else:
      if buttons != button_buffer[-1] :
        button_buffer.append(buttons)
                   
    # Keeping buffer size to max allowed
    if len(button_buffer) > JoystickController.__MAX_BUFFER_SIZE__:
      del button_buffer[0]   
    
    return button_buffer     
   
  def findMatchingMoves(self,move_list,button_sequence):
    matched_moves = []
    for move in move_list:      
      if move.match(button_sequence):
        matched_moves.append(move)
        if not move.is_submove:     
          break    
    
    return matched_moves  

            

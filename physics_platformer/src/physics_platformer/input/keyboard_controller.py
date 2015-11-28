from physics_platformer.input import ControllerInterface
from panda3d.core import BitMask32
import logging

class KeyboardButtons(object):
  
  __BIT_OFFSET__ = 1
  
  # directions
  NONE            =   BitMask32(0)          # bitarray('0000000000000000')
  DPAD_NONE       =   BitMask32.bit(__BIT_OFFSET__)      # bitarray('00000000000000000000000000000001')
  DPAD_UP         =   BitMask32.bit(1 + __BIT_OFFSET__)  # bitarray('00000000000000000000000000000001')
  DPAD_DOWN       =   BitMask32.bit(2 + __BIT_OFFSET__)  # bitarray('00000000000000000000000000000010') 
  DPAD_LEFT       =   BitMask32.bit(3 + __BIT_OFFSET__)  # bitarray('00000000000000000000000000000100')
  DPAD_RIGHT      =   BitMask32.bit(4 + __BIT_OFFSET__)  # bitarray('00000000000000000000000000001000')    
  DPAD_UPRIGHT    =   DPAD_UP | DPAD_RIGHT
  DPAD_UPLEFT     =   DPAD_UP | DPAD_LEFT
  DPAD_DOWNRIGHT  =   DPAD_DOWN | DPAD_RIGHT
  DPAD_DOWNLEFT   =   DPAD_DOWN | DPAD_LEFT
  
  # buttons
  KEY_A         =   BitMask32.bit(5 + __BIT_OFFSET__)  # bitarray('00000000000000000000000000010000')
  KEY_Q         =   BitMask32.bit(6 + __BIT_OFFSET__)  # bitarray('00000000000000000000000000100000')
  KEY_S         =   BitMask32.bit(7 + __BIT_OFFSET__)  # bitarray('00000000000000000000000001000000')
  KEY_W         =   BitMask32.bit(8 + __BIT_OFFSET__)  # bitarray('00000000000000000000000010000000')
  KEY_D         =   BitMask32.bit(9 + __BIT_OFFSET__)  # bitarray('00000000000000000000000100000000')
  KEY_E         =   BitMask32.bit(10 + __BIT_OFFSET__) # bitarray('00000000000000000000001000000000')
  KEY_X         =   BitMask32.bit(11 + __BIT_OFFSET__) # bitarray('00000000000000000000010000000000')
  KEY_C         =   BitMask32.bit(12 + __BIT_OFFSET__) # bitarray('00000000000000000000100000000000')
  KEY_Z         =   BitMask32.bit(13 + __BIT_OFFSET__) # bitarray('00000000000000000001000000000000')
  KEY_SPACE     =   BitMask32.bit(14 + __BIT_OFFSET__) # bitarray('00000000000000000010000000000000')
  KEY_SHIFT     =   BitMask32.bit(15 + __BIT_OFFSET__) # bitarray('00000000000000000100000000000000')
  KEY_ESC       =   BitMask32.bit(16 + __BIT_OFFSET__) # bitarray('00000000000000001000000000000000')
  KEY_F1        =   BitMask32.bit(17 + __BIT_OFFSET__) # bitarray('00000000000000010000000000000000')

class KeyboardController(ControllerInterface):  
  DEFAULT_BUFFER_TIMEOUT = 2 # 2 seconds
  DEFAULT_UPDATE_TIME = 0.1 # seconds  
  __MAX_BUFFER_SIZE__ = 30 
  
  def __init__(self,input_state,key_button_map, buffer_timeout = DEFAULT_BUFFER_TIMEOUT, update_time = DEFAULT_UPDATE_TIME):
    ControllerInterface.__init__(self)
    self.input_state_ = input_state
    self.key_button_map_ = key_button_map
    self.one_shot_mode_ = False
    
    # update members
    self.update_time_ = update_time
    self.buffer_timeout_ = buffer_timeout
    self.button_release_buffer_ = []
    self.button_press_buffer_ = []
    self.buffer_time_elapsed_ = 0
    self.update_time_elapsed_ = 0
    
    # history
    self.previous_down_buttons_ = KeyboardButtons.NONE
    
    self.input_state_.watchWithModifiers("right","arrow_right")
    self.input_state_.watchWithModifiers('left', 'arrow_left')
    self.input_state_.watchWithModifiers('up', 'arrow_up')
    self.input_state_.watchWithModifiers('down', 'arrow_down')
    
    for key in key_button_map.keys():
      self.input_state_.watchWithModifiers(key,key)
    
  def update(self,dt):
    
    # clear buffer after buffer timeout has elapsed
    self.buffer_time_elapsed_ = self.buffer_time_elapsed_ + dt
    if self.buffer_time_elapsed_ > self.buffer_timeout_:        
        self.reset()
    
    self.update_time_elapsed_+=dt    
    if self.update_time_elapsed_ > self.update_time_:
      self.update_time_elapsed_ = 0
    else:
      return
    
    direction_pressed = KeyboardButtons.NONE
    if self.input_state_.isSet('right'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_RIGHT

    if self.input_state_.isSet('left'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_LEFT

    if self.input_state_.isSet('up'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_UP

    if self.input_state_.isSet('down'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_DOWN
      
    if direction_pressed == KeyboardButtons.NONE:
      direction_pressed = KeyboardButtons.DPAD_NONE
    
    keys_down = KeyboardButtons.NONE  
    for key in self.key_button_map_.keys():
      if self.input_state_.isSet(key):
        keys_down = keys_down | self.key_button_map_[key]        
        #logging.info("Added key %s"%(key))
        
    # merge direction into keys down
    keys_down = keys_down | direction_pressed   
    
    # finding keys_pressed
    keys_pressed = keys_down & ~self.previous_down_buttons_  if self.one_shot_mode_ else keys_down    

    # finding released buttons
    keys_released = ~keys_down & self.previous_down_buttons_
            
    # Saving buttons pressed into buffer      
    self.button_press_buffer_ = self.storeIntoBuffer(self.button_press_buffer_, keys_pressed)
    self.button_release_buffer_ = self.storeIntoBuffer(self.button_release_buffer_, keys_released)
    
    # storing last button presses
    self.previous_down_buttons_ = keys_down
    
    # checking button combinations for button press matches
    matched_moves = self.findMatchingMoves(self.button_press_moves_,self.button_press_buffer_)
    for move in matched_moves:
      move.execute()
      if not move.is_submove:
        self.reset() # clear buffer
        break
      
    # checking button combinations for button release matches
    matched_moves = self.findMatchingMoves(self.button_release_moves_,self.button_release_buffer_)
    for move in matched_moves:
      move.execute()
      if not move.is_submove:
        self.button_release_buffer_ = []
        break
      
  def storeIntoBuffer(self, button_buffer,buttons):
    
    # Saving buttons into buffer      
    if (len(button_buffer) == 0):            
      button_buffer.append(buttons)
    else:
      if buttons != button_buffer[-1]:
        button_buffer.append(buttons)
                   
    # Keeping buffer size to max allowed
    if len(button_buffer) > KeyboardController.__MAX_BUFFER_SIZE__:
      del button_buffer[0]   
    
    return button_buffer  
      
  def reset(self): 
    self.buffer_time_elapsed_ = 0
    self.button_press_buffer_ = [] 
    
  def findMatchingMoves(self,move_list,button_sequence):
    matched_moves = []
    for move in move_list:      
      if move.match(button_sequence):
        matched_moves.append(move)
        if not move.is_submove:     
          break    
    
    return matched_moves
          
      
      
        
    

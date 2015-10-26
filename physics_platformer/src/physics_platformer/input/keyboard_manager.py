from physics_platformer.input import InputManager
from panda3d.core import BitMask32
import logging

class KeyboardButtons(object):
  
  __BIT_OFFSET__ = 0
  
  # directions
  NONE            =   BitMask32()  # bitarray('0000000000000000')
  DPAD_UP         =   BitMask32.bit(1 + __BIT_OFFSET__)  # bitarray('0000000000000001')
  DPAD_DOWN       =   BitMask32.bit(2 + __BIT_OFFSET__)  # bitarray('0000000000000010') 
  DPAD_LEFT       =   BitMask32.bit(3 + __BIT_OFFSET__)  # bitarray('0000000000000100')
  DPAD_RIGHT      =   BitMask32.bit(4 + __BIT_OFFSET__)  # bitarray('0000000000001000')    
  DPAD_UPRIGHT    =   DPAD_UP | DPAD_RIGHT
  DPAD_UPLEFT     =   DPAD_UP | DPAD_LEFT
  DPAD_DOWNRIGHT  =   DPAD_DOWN | DPAD_RIGHT
  DPAD_DOWNLEFT   =   DPAD_DOWN | DPAD_LEFT
  
  # buttons
  KEY_A         =   BitMask32.bit(5 + __BIT_OFFSET__)  # bitarray('0000000000010000')
  KEY_Q         =   BitMask32.bit(6 + __BIT_OFFSET__)  # bitarray('0000000000100000')
  KEY_S         =   BitMask32.bit(7 + __BIT_OFFSET__)  # bitarray('0000000001000000')
  KEY_W         =   BitMask32.bit(8 + __BIT_OFFSET__)  # bitarray('0000000010000000')
  KEY_D         =   BitMask32.bit(9 + __BIT_OFFSET__)  # bitarray('0000000100000000')
  KEY_E         =   BitMask32.bit(10 + __BIT_OFFSET__) # bitarray('0000001000000000')
  KEY_X         =   BitMask32.bit(11 + __BIT_OFFSET__) # bitarray('0000010000000000')
  KEY_C         =   BitMask32.bit(12 + __BIT_OFFSET__) # bitarray('0000100000000000')
  KEY_SPACE     =   BitMask32.bit(13 + __BIT_OFFSET__) # bitarray('0001000000000000')
  KEY_SHIFT     =   BitMask32.bit(14 + __BIT_OFFSET__) # bitarray('0010000000000000')
  KEY_ESC       =   BitMask32.bit(15 + __BIT_OFFSET__) # bitarray('0010000000000000')

class KeyboardManager(InputManager):  
  __DEFAULT_BUFFER_TIMEOUT__ = 2 # 2 seconds
  __MAX_BUFFER_SIZE__ = 30 
  
  def __init__(self,input_state,key_button_map, buffer_timeout = __DEFAULT_BUFFER_TIMEOUT__):
    InputManager.__init__(self)
    self.input_state_ = input_state
    self.key_button_map_ = key_button_map
    
    # update members
    self.buffer_timeout_ = buffer_timeout
    self.button_buffer_ = []
    self.time_elapsed_ = 0
    
    self.input_state_.watchWithModifiers("right","arrow_right")
    self.input_state_.watchWithModifiers('left', 'arrow_left')
    self.input_state_.watchWithModifiers('up', 'arrow_up')
    self.input_state_.watchWithModifiers('down', 'arrow_down')
    
    for key in key_button_map.keys():
      self.input_state_.watchWithModifiers(key,key)
    
  def update(self,dt):
    
    # clear buffer after buffer timeout has elapsed
    self.time_elapsed_ = self.time_elapsed_ + dt
    if self.time_elapsed_ > self.buffer_timeout_:        
        self.reset()
        
    
    direction_pressed = KeyboardButtons.NONE
    if self.input_state_.isSet('right'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_RIGHT

    if self.input_state_.isSet('left'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_LEFT

    if self.input_state_.isSet('up'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_UP

    if self.input_state_.isSet('down'): 
      direction_pressed = direction_pressed | KeyboardButtons.DPAD_DOWN
    
    keys_pressed = KeyboardButtons.NONE  
    for key in self.key_button_map_.keys():
      if self.input_state_.isSet(key):
        keys_pressed = keys_pressed | self.key_button_map_[key]        
        #logging.info("Added key %s"%(key))
        
    # merge direction into keys pressed
    if direction_pressed != KeyboardButtons.NONE:
      keys_pressed = keys_pressed | direction_pressed      
      
    # Saving buttons pressed into buffer      
    #logging.info("Keys pressed bitmask: %s"%(str(keys_pressed)))  
    if (len(self.button_buffer_) == 0):            
        self.button_buffer_.append(keys_pressed)
    else:
        if keys_pressed != self.button_buffer_[-1]:
            self.button_buffer_.append(keys_pressed)
            
            
    # Keeping buffer size to max allowed
    if len(self.button_buffer_) > KeyboardManager.__MAX_BUFFER_SIZE__:
        del self.button_buffer_[0]      
      
    # checking direction matches
    #self.checkMatches([direction_pressed])
    
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
          
      
      
        
    

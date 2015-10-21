from physics_platformer.input import InputManager

class KeyboardButtons(object):
  
  __BIT_OFFSET__ = 0
  
  # directions
  NONE            =   BitMask32.bit(0 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000000000000')
  DPAD_UP         =   BitMask32.bit(1 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000000000001')
  DPAD_DOWN       =   BitMask32.bit(2 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000000000010') 
  DPAD_LEFT       =   BitMask32.bit(3 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000000000100')
  DPAD_RIGHT      =   BitMask32.bit(4 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000000001000')    
  DPAD_UPRIGHT    =   DPAD_UP | DPAD_RIGHT
  DPAD_UPLEFT     =   DPAD_UP | DPAD_LEFT
  DPAD_DOWNRIGHT  =   DPAD_DOWN | DPAD_RIGHT
  DPAD_DOWNLEFT   =   DPAD_DOWN | DPAD_LEFT
  
  # buttons
  BUTTON_A        =   BitMask32.bit(5 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000000010000')
  BUTTON_B        =   BitMask32.bit(6 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000000100000')
  BUTTON_X        =   BitMask32.bit(7 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000001000000')
  BUTTON_Y        =   BitMask32.bit(8 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000010000000')
  TRIGGER_R1      =   BitMask32.bit(9 + KeyboardButtons.__BIT_OFFSET__)  # bitarray('0000000100000000')
  TRIGGER_R2      =   BitMask32.bit(10 + KeyboardButtons.__BIT_OFFSET__) # bitarray('0000001000000000')
  TRIGGER_L1      =   BitMask32.bit(11 + KeyboardButtons.__BIT_OFFSET__) # bitarray('0000010000000000')
  TRIGGER_L2      =   BitMask32.bit(12 + KeyboardButtons.__BIT_OFFSET__) # bitarray('0000100000000000')
  BUTTON_START    =   BitMask32.bit(13 + KeyboardButtons.__BIT_OFFSET__) # bitarray('0001000000000000')
  BUTTON_SELECT   =   BitMask32.bit(14 + KeyboardButtons.__BIT_OFFSET__) # bitarray('0010000000000000')

class KeyboardManager(InputManager):
  
  def __init__(self,input_state,key_button_map):
    InputManager.__init__()
    self.input_state_ = input_state
    self.key_button_map_ = key_button_map
    
    self.input_state_.watchWithModifiers("right","arrow_right")
    self.input_state_.watchWithModifiers('left', 'arrow_left')
    self.input_state_.watchWithModifiers('up', 'arrow_up')
    self.input_state_.watchWithModifiers('down', 'arrow_down')
    
  def update(self,dt):
    
    direction_button = KeyboardButtons.NONE
    if self.input_state_.isSet('right'): 
      direction_button = direction_button | KeyboardButtons.DPAD_RIGHT

    if self.input_state_.isSet('left'): 
      direction_button = direction_button | KeyboardButtons.DPAD_LEFT

    if self.input_state_.isSet('up'): 
      direction_button = direction_button | KeyboardButtons.DPAD_UP

    if self.input_state_.isSet('down'): 
      direction_button = direction_button | KeyboardButtons.DPAD_DOWN
    
  
from panda3d.core import BitMask32

class JoystickButtons(object):
  
  __BIT_OFFSET__ = 0 
    
  # directions
  NONE            =   BitMask32(0)  # bitarray('0000000000000000')
  DPAD_UP         =   BitMask32.bit(1 + __BIT_OFFSET__)  # bitarray('0000000000000001')
  DPAD_DOWN       =   BitMask32.bit(2 + __BIT_OFFSET__)  # bitarray('0000000000000010') 
  DPAD_LEFT       =   BitMask32.bit(3 + __BIT_OFFSET__)  # bitarray('0000000000000100')
  DPAD_RIGHT      =   BitMask32.bit(4 + __BIT_OFFSET__)  # bitarray('0000000000001000')    
#   DPAD_UPRIGHT    =   DPAD_UP | DPAD_RIGHT
#   DPAD_UPLEFT     =   DPAD_UP | DPAD_LEFT
#   DPAD_DOWNRIGHT  =   DPAD_DOWN | DPAD_RIGHT
#   DPAD_DOWNLEFT   =   DPAD_DOWN | DPAD_LEFT
  DPAD_UPRIGHT    =   BitMask32.bit(17 + __BIT_OFFSET__)
  DPAD_UPLEFT     =   BitMask32.bit(18 + __BIT_OFFSET__)
  DPAD_DOWNRIGHT  =   BitMask32.bit(19 + __BIT_OFFSET__)
  DPAD_DOWNLEFT   =   BitMask32.bit(20 + __BIT_OFFSET__)
  
  # buttons
  BUTTON_A        =   BitMask32.bit(5 + __BIT_OFFSET__)  # bitarray('0000000000010000')
  BUTTON_B        =   BitMask32.bit(6 + __BIT_OFFSET__)  # bitarray('0000000000100000')
  BUTTON_X        =   BitMask32.bit(7 + __BIT_OFFSET__)  # bitarray('0000000001000000')
  BUTTON_Y        =   BitMask32.bit(8 + __BIT_OFFSET__)  # bitarray('0000000010000000')
  TRIGGER_R1      =   BitMask32.bit(9 + __BIT_OFFSET__)  # bitarray('0000000100000000')
  TRIGGER_R2      =   BitMask32.bit(10 + __BIT_OFFSET__) # bitarray('0000001000000000')
  TRIGGER_L1      =   BitMask32.bit(11 + __BIT_OFFSET__) # bitarray('0000010000000000')
  TRIGGER_L2      =   BitMask32.bit(12 + __BIT_OFFSET__) # bitarray('0000100000000000')
  BUTTON_START    =   BitMask32.bit(13 + __BIT_OFFSET__) # bitarray('0001000000000000')
  BUTTON_SELECT   =   BitMask32.bit(14 + __BIT_OFFSET__) # bitarray('0010000000000000')
  TRIGGER_R3      =   BitMask32.bit(15 + __BIT_OFFSET__) # bitarray('0000000100000000')
  TRIGGER_L3      =   BitMask32.bit(16 + __BIT_OFFSET__) # bitarray('0000001000000000')
    
    
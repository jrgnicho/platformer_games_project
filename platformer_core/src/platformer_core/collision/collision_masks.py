from panda3d.core import BitMask32

class CollisionMasks(object):
  
  # General
  NO_COLLISION        = BitMask32.allOff()
  ALL                 = BitMask32.allOn()
  
  # Game Object
  GAME_OBJECT_RIGID_BODY    = BitMask32.bit(2)
  ATTACK_HIT                = BitMask32.bit(3)      # Character delivers attack
  ATTACK_DAMAGE             = BitMask32.bit(4)      # Character recieves attack
  GAME_OBJECT_BOTTOM        = BitMask32.bit(5)
  GAME_OBJECT_LEFT          = BitMask32.bit(6)
  GAME_OBJECT_RIGHT         = BitMask32.bit(7)
  GAME_OBJECT_TOP           = BitMask32.bit(8)
  ACTION_TRIGGER_0          = BitMask32.bit(9)     # Mainly used to detect sector transitions
  ACTION_TRIGGER_1          = BitMask32.bit(10)      # Reserved for Special Purpose Ghost nodes
  ACTION_TRIGGER_2          = BitMask32.bit(11)      # Reserved for Special Purpose Ghost nodes
  ACTION_TRIGGER_3          = BitMask32.bit(12)      # Reserved for Special Purpose Ghost nodes
  
  
  # Environment  
  POWERUP             = BitMask32.bit(20)
  PLATFORM_RIGID_BODY = BitMask32.bit(21)
  LEDGE               = BitMask32.bit(22)     # Characters can hang from it and climb onto platform
  LEVEL_BOUND         = BitMask32.bit(23)  
  PEG                 = BitMask32.bit(24)     # Characters can hang from it
  SURFACE             = BitMask32.bit(25)     # Characters can land on it
  WALL                = BitMask32.bit(26)
  CEILING             = BitMask32.bit(27)     # Usually the bottom of a surface
  SECTOR_TRANSITION   = BitMask32.bit(28)
  
  
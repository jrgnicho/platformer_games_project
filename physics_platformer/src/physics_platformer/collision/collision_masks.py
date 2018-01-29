from panda3d.core import BitMask32

class CollisionMasks(object):
  
  # General
  NO_COLLISION        = BitMask32.allOff()
  ALL                 = BitMask32.allOn()
  
  # Game Object
  GAME_OBJECT_AABB    = BitMask32.bit(2)
  ATTACK_HIT          = BitMask32.bit(3)      # Character delivers attack
  ATTACK_DAMAGE       = BitMask32.bit(4)      # Character recieves attack
  ACTION_TRIGGER         = BitMask32.bit(5)
  GAME_OBJECT_BOTTOM  = BitMask32.bit(8)
  GAME_OBJECT_LEFT    = BitMask32.bit(9)
  GAME_OBJECT_RIGHT   = BitMask32.bit(10)
  GAME_OBJECT_TOP     = BitMask32.bit(11)
  GAME_OBJECT_ORIGIN  = BitMask32.bit(12)
  
  
  # Environment  
  POWERUP             = BitMask32.bit(20)
  LEVEL_OBSTACLE      = BitMask32.bit(21)
  LEDGE               = BitMask32.bit(22)
  LEVEL_BOUND         = BitMask32.bit(23)  
  LEVEL_PEG           = BitMask32.bit(24)     # Characters can hang from it
  SURFACE             = BitMask32.bit(25)     # Characters can land on it
  WALL                = BitMask32.bit(26)
  CEILING             = BitMask32.bit(27)
  SECTOR_TRANSITION   = BitMask32.bit(28)
  
  
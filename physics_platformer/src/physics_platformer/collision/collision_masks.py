from panda3d.core import BitMask32

class CollisionMasks(object):
  
  # General
  NO_COLLISION        = BitMask32.allOff()
  ALL                 = BitMask32.allOn()
  
  # Game Object
  GAME_OBJECT_AABB    = BitMask32.bit(2)
  ATTACK_HIT          = BitMask32.bit(3)
  ATTACK_DAMAGE       = BitMask32.bit(4)
  ACTION_BODY         = BitMask32.bit(5)
  GAME_OBJECT_BOTTOM  = BitMask32.bit(8)
  GAME_OBJECT_LEFT    = BitMask32.bit(9)
  GAME_OBJECT_RIGHT   = BitMask32.bit(10)
  GAME_OBJECT_TOP     = BitMask32.bit(11)
  GAME_OBJECT_ORIGIN  = BitMask32.bit(12)
  
  
  # Level  
  POWERUP             = BitMask32.bit(20)
  LEVEL_OBSTACLE      = BitMask32.bit(21)
  LEDGE               = BitMask32.bit(22)
  LEVEL_BOUND         = BitMask32.bit(23)  
  LEVEL_PEG           = BitMask32.bit(24)     # Characters can hang from it
  LANDING_SURFACE     = BitMask32.bit(25)     # Characters can land on it
  SECTOR_TRANSITION   = BitMask32.bit(26)
  
  
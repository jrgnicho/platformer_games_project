from panda3d.core import BitMask32

class CollisionMasks(object):
  
  NO_COLLISION = BitMask32.allOff()
  ALL = BitMask32.allOn()
  LEVEL_OBSTACLE = BitMask32.bit(1)
  RIGID_BODY = BitMask32.bit(2)
  ATTACK_HIT = BitMask32.bit(3)
  ATTACK_COLLISION = BitMask32.bit(4)
  ACTION_BODY = BitMask32.bit(5)
  POWERUP = BitMask32.bit(6)
  LEDGE = BitMask32.bit(7)
  LANDING_SURFACE = BitMask32.bit(8)
  LEFT_WALL_SURFACE = BitMask32.bit(9)
  RIGHT_WALL_SURFACE = BitMask32.bit(10)
  CEILING_SURFACE = BitMask32.bit(11)
  LEVEL_BOUND = BitMask32.bit(12)
  
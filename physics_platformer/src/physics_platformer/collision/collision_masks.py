from panda3d.core import BitMask32

class CollisionMasks(object):
  
  NO_COLLISION = BitMask32.allOff()
  ALL = BitMask32.allOn()
  LEVEL_OBSTACLE = BitMask32.bit(1)
  GAME_OBJECT_AABB = BitMask32.bit(2)
  ATTACK_HIT = BitMask32.bit(3)
  ATTACK_DAMAGE = BitMask32.bit(4)
  ACTION_BODY = BitMask32.bit(5)
  POWERUP = BitMask32.bit(6)
  LEDGE = BitMask32.bit(7)
  GAME_OBJECT_BOTTOM = BitMask32.bit(8)
  GAME_OBJECT_LEFT = BitMask32.bit(9)
  GAME_OBJECT_RIGHT = BitMask32.bit(10)
  GAME_OBJECT_TOP = BitMask32.bit(11)
  LEVEL_BOUND = BitMask32.bit(12)
  
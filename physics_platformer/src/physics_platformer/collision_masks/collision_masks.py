from panda3d.core import BitMask32

class CollisionMasks(object):
  
  LEVEL = BitMask32.bit(1)
  RIGID_BODY = BitMask32.bit(2)
  ATTACK_HIT = BitMask32.bit(3)
  ATTACK_COLLISION = BitMask32.bit(4)
  ACTION_BODY = BitMask32.bit(5)
  POWERUP = BitMask32.bit(6)
  
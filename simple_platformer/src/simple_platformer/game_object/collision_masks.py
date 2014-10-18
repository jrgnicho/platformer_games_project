from bitarray import bitarray
class CollisionMasks(object):
    
    DEFAULT =   bitarray('00000000')
    PLAYER =    bitarray('00000001')
    PLATFORM =  bitarray('00000010')
    ENEMY =     bitarray('00000100')
    POWERUP =   bitarray('00001000')
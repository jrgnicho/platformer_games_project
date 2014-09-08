class AttackTypes(object):
    
    SUBORDINATE = 'SUBORDINATE'  # Its movement and behavior is coupled to the player that spawned it
    SOVEREIGN = 'SOVEREING'     # Its movement and behavior is independent from the player that spawned it
    
class MotionModes(object):
    
    PLAYER = 'PLAYER'
    DIRECTION = 'DIRECTION'
    PATH = 'PATH'
    PURSUIT = 'PURSUIT'     
    
    
class LifeSpanModes(object):
    
    TIME_LIMIT = 'TIME_LIMIT'
    RANGE_LIMIT = 'RANGE_LIMIT'
    HEALTH_DEPLETION = 'HEALTH_DEPLETION'
    INFINITE = 'INFINITE'
    HEALTH_AND_TIME = 'HEALTH_AND_TIME'
    HEALTH_AND_RANGE = 'HEALTH_AND_RANGE'
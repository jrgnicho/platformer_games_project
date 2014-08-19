class AttackTypes(object):
    
    SUBORDINATE = 'SUBORDINATE'  # Its movement and behavior is coupled to the player that spawned it
    SOVEREIGN = 'SOVEREING'     # Its movement and behavior is independent from the player that spawned it
    
class MotionModes(object):
    
    PLAYER = 'PLAYER'
    DIRECTION = 'DIRECTION'
    PATH = 'PATH'
    PURSUIT = 'PURSUIT'
    
class LayerDrawPriorityTypes(object):
    
    DEFAULT = 0
    LEVEL_BACKGROUND = 0,
    LEVEL_REAR_LAYER = 1 # platforms
    LEVEL_MIDDLE_LAYER = 2    
    LEVEL_FRONT = 3 
    ENEMY_LAYER = 2
    PLAYER_REAR_EFFECTS_LAYER = 3
    PLAYER_LAYER = 4  # player images
    PLAYER_FRONT_EFFECTS_LAYER = 5 # player effects in front
    
    
class LifeSpanModes(object):
    
    TIME_LIMIT = 'TIME_LIMIT'
    RANGE_LIMIT = 'RANGE_LIMIT'
    HEALTH_DEPLETION = 'HEALTH_DEPLETION'
    INFINITE = 'INFINITE'
    HEALTH_AND_TIME = 'HEALTH_AND_TIME'
    HEALTH_AND_RANGE = 'HEALTH_AND_RANGE'
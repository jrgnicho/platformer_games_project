from game_assets.properties import MotionModes
from game_assets.properties import LifeSpanModes
from pygame import Rect

class HitProperties(object):
    
    def __init__(self):
        
        self.force_applied = (0,0) # (x,y) tuple
        self.damage_per_hit = 0
        self.max_hits_allowed = 0
        
class MotionProperties(object):
    
    def __init__(self):
        
        self.motion_mode = MotionModes.PLAYER
        self.direction = (0,0) # dx,dy tuple indicative of the position change increment per animation frame
        self.path = [(0,0), (0,0)] # list of (dx,dy) tuples indicative of the position change per animation frame
        self.pursuit_speed = (0,0) # max position change allowed in x and y
        self.pursuit_direction_change = 0.0 # percentage threshold of applied to the required rotation angle needed to stay in pursuit
        
class LifeSpanProperties(object):
    
    def __init__(self):
        
        self.health = 0
        self.life_span_mode = LifeSpanModes.HEALTH_DEPLETION
        self.time_limit = 0 # time in miliseconds
        self.range_rect = Rect(0,0,0,0)
        self.activation_frame_index = 0 # the attack emerges when the spawning object's (usually player)
                                        # image frame with this index is being played
        
        
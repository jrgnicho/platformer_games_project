from combat_platformer.combat import *
import pygame
from pygame.sprite import Sprite
from pygame import Rect

class StrikeProperties(object):
    
    def __init__(self):
        
        self.force_applied = (0,0) # (x,y) tuple
        self.damage_points = 0
        self.max_strikes = 0
        self.strike_rects = []
        
class MotionProperties(object):
    
    def __init__(self):
        
        self.motion_mode = MotionModes.PLAYER
        self.direction = (0,0) # dx,dy tuple indicative of the position change increment per animation frame
        self.path = [(0,0), (0,0)] # list of (dx,dy) tuples indicative of the position change per animation frame
        self.pursuit_speed = (0,0) # max position change allowed in x and y
        self.pursuit_direction_change = 0.0 # percentage threshold of applied to the required rotation angle needed to stay in pursuit
      
      

class LifeSpanProperties(object):
    """
        This class contains properties applicable to SOVEREIGN attack types which act independently of the 
        player (parent object) that spawned it.
    """  
    
    def __init__(self):
        
        self.health = 0
        self.life_span_mode = LifeSpanModes.HEALTH_DEPLETION
        self.time_limit = 0 # time in miliseconds
        self.activation_frame_index = 0 # the attack emerges when the spawning object's (usually player)
                                        # image frame with this index is being played
                                        
                                        

class Attack(object) :
    
    def __init__(self):
        
        State.__init__(self)        
        
        self.__collision_sprite = pygame.sprite.Sprite() # Use the pygame.sprite.groupcollide() to detect when the strike lands
        self.__collision_sprite.rect = pygame.Rect(0,0,0,0)
        self.parent_object = None # reference to object that spawned this attack, when set it shold be of type Animatable object
        
        # attack attributes
        self.type = AttackTypes.SUBORDINATE
        self.strikes = [] # array of strike property objects, one per animation frame
        self.motion = MotionProperties()
        self.life_span = LifeSpanProperties()
        self.current_index = 0; # used to index into the "strikes" member
    
    """
        Collision Sprite property which is the unions of all strike rectangles
    """
    @property    
    def collision_sprite(self):
        
        # used union of all active strike rectangles
        self.__collision_sprite.rect.unionall_ip(self.strikes[0].strike_rects)
        
        # set location using parents location
        parent_rect = self.parent_object.collision_sprite.rect
        if self.parent_object != None:            
            self.__collision_sprite.rect.topleft = parent_rect.topleft
            
        #endif
        
        return self.__collision_sprite
    
    """
    update : Empty placeholder for subclass that performs some custom logic
    """
    def update(self):
        pass
    
    """
    draw : Empty placeholder for subclass attacks that have animation sequences while the attack is active
    """
    def draw(self):
        pass
        
        
        
        
 
        
    
        
        
        
        
        
        

                                       
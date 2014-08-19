from pygame import Rect
from pygame.sprite import Sprite
from game_assets.object_assets import AnimationAssets
from game_assets.object_assets import AttackCollisionAssets
from game_assets.properties import AttackTypes
from game_assets.properties import MotionProperties
from game_assets.properties import LifeSpanProperties

class PlayerActionAssets(object):
    """
    This class contains the necessary assets to control a player's object's animations an perform
    collision detection checks corresponding to this action
    """
    
    def __init__(self):
        
        self.key = 'NONE'
        self.animation = AnimationAssets()
        self.collision = CollisionSpriteGroup()
        self.attack_keys = [] # keys to attacks that this action can spawn
        
        
class AttackActionAssets(object):
    
    def __init__(self):
        
        self.key= 'NONE'
        self.animation = AnimationAssets()
        self.collision_hits = AttackCollisionAssets()
        self.attack_keys = []
        self.attack_type = AttackTypes.SUBORDINATE  
               
        # motion properties
        self.motion_properties = MotionProperties()
        
        # life span properties
        self.life_span_properties = LifeSpanProperties()
from pygame import Rect
from pygame.sprite import Sprite
from game_asset_management.object_assets import AnimationAssets
from game_asset_management.object_assets import CollisionAssets
from game_asset_management.object_assets import HitAssets
from game_asset_management.properties import AttackTypes
from game_asset_management.properties import MotionProperties
from game_asset_management.properties import LifeSpanProperties

class AttackAssets(object):
    
    def __init__(self):

        self.hits = [] # list of HitAssets
        self.attack_type = AttackTypes.SUBORDINATE  
               
        # motion properties
        self.motion_properties = MotionProperties()
        
        # life span properties
        self.life_span_properties = LifeSpanProperties()
        
        # extras
        self.extra_attributes = {}

class ObjectAssets(object):
    """
    This class contains the necessary assets to control a player's object's animations an perform
    collision detection checks corresponding to this action
    """
    
    def __init__(self):
        
        self.asset_set = ''
        self.key = 'NONE'
        self.animation = AnimationAssets()
        self.collision = CollisionAssets()
        self.attack_keys = [] # keys to other attacks that this action can spawn
        self.extra_attributes = {}
        self.attack = AttackAssets()
        
        

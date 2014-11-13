from simple_platformer.utilities import Colors
from simple_platformer.game_object import GameObject
from combat_platformer.combat import *
import pygame
from pygame.sprite import Sprite
from pygame import Rect
from orca.dbusserver import obj

class StrikeProperties(object):
    
    def __init__(self):
        
        self.force_applied = (0,0) # (x,y) tuple
        self.damage_points = 0
        self.max_hits = 0
        
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
                                        
                                        
class Hit(pygame.sprite.Sprite):
    
    """ 
    Hit(parent,rect,offset)
        - parent: Parent game object that spawns the attack (usually the player or an enemy
        - rect: The pygame.Rect object that will be used to check the hit.  
        - offset: tuple (x,y) indicating the position of the rect relative to the parent object's center
    """    
    def __init__(self,parent,rect,offset):
        
        pygame.sprite.Sprite.__init__(self)
        self.parent_object = parent
        self.__rect__ = pygame.Rect(rect)
        self.__offset__ = offset
        self.image = pygame.Surface([self.__rect__.width,self.__rect__.height])
        self.image.fill(Colors.WHITE)
        self.layer = GameObject.Layer.FRONT
        
    @property
    def rect(self):
        
        cx = self.parent_object.centerx + self.__offset__[0]
        cy = self.parent_object.centery + self.__offset__[1]
        self.__rect__.center = (cx,cy)
        return self.__rect__
        
        
class Strike(object):
    
    def __init__(self,parent,mask_surface,properties = StrikeProperties()):
        pygame.sprite.OrderedUpdates.__init__(self)
        self.parent_object = parent
        
        # sprite that represents the reach of all hit rectangles
        self.range_sprite = None
        
        # hits array
        self.hits = []
        
        
        ## creating hit objects and range sprite
        mask = pygame.mask.from_surface(mask_surface, 127)
        parent_rect = mask_surface.get_rect()
        
        rects = mask.get_bounding_rects()
        for r in iter(rects):
            offsetx = r.centerx  - parent_rect.centerx 
            offsety = r.centery - parent_rect.centery 
            hit = Hit(self.parent_object,r,(offsetx,offsety))
            self.hits.append(hit)
        #endfor  
        
        # creating range sprite 
        if len(rects) > 0:
            self.range_sprite = pygame.sprite.Sprite()
            self.range_sprite.rect = pygame.Rect.unionall(rects)
        #endif
                                       

class Attack(object) :
    """
    Attack(parent,mask_images)
    - parent: Parent game object that spawns the attack (usually the player or an enemy
    - mask_images: The images containing the pixels from which the attack collision masks will be created.  
    - strike_properties: (optional) Property object used in each strike in this attack.
    """
    
    def __init__(self,parent,images,strike_properties = StrikeProperties()):
               
        
        self.parent_object = parent # reference to object that spawned this attack, it should be a GameObject type      
        
        # attack attributes
        self.type = AttackTypes.SUBORDINATE
        self.strikes = [] # array of strike property objects, one per animation frame
        self.motion_properties = MotionProperties()
        self.life_span_properties = LifeSpanProperties()
        self.strike_index = 0; # used to index into the "strikes" member
        
        # active hits (sprites)
        self.active_hits = pygame.sprite.Group()
        
        # initializing strikes array
        for im in iter(images):
            
            strk = Strike(parent, im, strike_properties)
            self.strikes.append(strk)
        #endfor
        
    def activate(self):
        
        self.strike_index = 0
        self.active_hits.empty()        
        self.select_strike(self.paren_object.animation_frame_index)
        
    def deactivate(self):
        
        if len(self.strikes) > 0:
                        
            # cleanup
            strike = self.strikes[self.strike_index]
            for hit in strike.hits:                
                hit.kill()
            #endfor
            
            self.parent_object.remove_range_sprite(strike.range_sprite)
        #endif
        
    
    """
    This method should be called when an animation sprite changes
    """    
    def select_strike(self,index):
        
        if len(self.strikes) > index:
            
            # activating strike's hit objects
            self.strike_index = index
            strk = self.strikes[index]
            self.active_hits.empty()
            self.active_hits.add(strk.hits)
            
            # adding hit objects to game object drawable sprites
            self.parent_object.drawable_group.add(strk.hits)
            
            # remove last strike range sprite
            if self.strike_index >0:
                prev_strike = self.strikes[index - 1]
                self.parent_object.remove_range_sprite(prev_strike.range_sprite)
            
            # add strike range sprite            
            self.parent_object.add_range_sprite(strk.range_sprite)
            
    def check_hits(self,game_object):
        
        hits = pygame.sprite.spritecollide(game_object, self.active_hits, False)
        for hit in iter(hits):
            hit.kill()
        #end

        
        
        
        
 
        
    
        
        
        
        
        
        

                                       
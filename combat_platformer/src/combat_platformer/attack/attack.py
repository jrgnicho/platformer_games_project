from simple_platformer.utilities import Colors
from simple_platformer.game_object import AnimationSprite
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
    def __init__(self):
        
        pygame.sprite.Sprite.__init__(self,parent,mask,offset)
        self.parent_object = parent
        self.mask = mask
        self.__rect__ = pygame.Rect((0,0),mask.get_size())
        self.offset = offset
        self.image = pygame.Surface([self.__rect__.width,self.__rect__.height]).convert_alpha()        
        self.__draw_mask__()
        self.layer = GameObject.Layer.FRONT
        
        # creating drawable sprite
        self.drawable_sprite = AnimationSprite(self.image,self.offset)
        
    def __draw_mask__(self):
        self.image.fill(Colors.GREEN)
        self.image.lock()
        h = self.__rect__.height
        w = self.__rect__.width
        bit = 0
        for i in range(0,w):
            for j in range(0,h):
                bit = self.mask.get_at(i,j)
                if bit == 0: # set transparent
                    self.image.set_at([0,0,0,0])
                #endif
            #endfor
        #endfor
        self.image.unlock()     
        
    def update(self):
        
        self.drawable_sprite.centerx = self.parent_object.screen_centerx 
        self.drawable_sprite.bottom =  self.parent_object.screen_bottom            
        
    @property
    def rect(self):
        
        cx = self.parent_object.rect.centerx + self.offset[0]
        cy = self.parent_object.rect.bottom + self.offset[1]
        self.__rect__.center = (cx,cy)
        return self.__rect__
    
            
    def kill(self):        
        self.drawable_sprite.kill()
                    
        
        
class Strike(object):
    
    def __init__(self,parent,animation_sprite,properties = StrikeProperties()):
        pygame.sprite.OrderedUpdates.__init__(self)
        self.parent_object = parent
        
        # sprite that represents the reach of all hit rectangles
        self.range_sprite = None
        
        # drawable group
        self.drawable_sprites = []
        
        # hits array
        self.hits = []        
        
        ## creating hit objects and range sprite
        mask = pygame.mask.from_surface(animation_sprite.image)
        parent_rect = animation_sprite.rect
        
        masks = mask.connected_components()
        
        if len(mask) > 0:
            for m in masks:
                hit = Hit(parent,m,animation_sprite.offset)
                self.hits.append(hit)
                self.drawable_sprites.append(hit.drawable_sprite)
            #endfor
            
            self.range_sprite = pygame.sprite.Sprite()
            self.range_sprite.rect = pygame.Rect((0,0),mask.get_size())
        #endif
        
        def len(self):
            return len(self.hits)
                   

class Attack(object) :
    """
    Attack(parent,mask_images)
    - parent: Parent game object that spawns the attack (usually the player or an enemy
    - mask_images: The images containing the pixels from which the attack collision masks will be created.  
    - strike_properties: (optional) Property object used in each strike in this attack.
    - index_strike_bounds: (optional) A 2 element tuple of the form (min_index,max_index) that limits the number of strikes
        that can be active.  Defaults to (0,len(mask_images) - 1)
    """
    
    def __init__(self,parent,sprite_set,strike_properties = StrikeProperties(),strike_index_bounds = None):
               
        
        self.parent_object = parent # reference to object that spawned this attack, it should be a GameObject type      
        
        # attack attributes
        self.type = AttackTypes.SUBORDINATE
        self.strikes = [] # array of strike property objects, one per animation frame
        self.motion_properties = MotionProperties()
        self.life_span_properties = LifeSpanProperties()
        self.strike_index = -1; # used to index into the "strikes" member
        self.strike_index_bounds = (0,len(images)-1) if strike_index_bounds == None else strike_index_bounds.copy()
        
        # active hits (sprites)
        self.active_hits = pygame.sprite.Group()
        
        # initializing strikes array
        for sp in iter(sprite_set.sprites):
            
            strk = Strike(parent, sp, strike_properties)
            self.strikes.append(strk)
        #endfor
        
    def strike_count(self):        
        return len(self.strikes)
        
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
            self.strike_index = -1
            self.parent_object.remove_range_sprite(strike.range_sprite)
        #endif
                
    
    """
    This method should be called when an animation sprite changes
    """    
    def select_strike(self,index):
        
        
        if self.strike_index_bounds[0] > index or self.strike_index_bounds[1] < index:
            return False
        #endif
        
        if self.strike_index == index:
            return True;
        #endif
        
        if (len(self.strikes) > index) :    
            
            # remove last strike range sprite
            if self.strike_index >= 0 and len(self.strikes[self.strike_index ]) > 0:
                prev_strike = self.strikes[self.strike_index ]
                self.parent_object.remove_range_sprite(prev_strike.range_sprite)       
                self.parent_object.drawable_group.remove(prev_strike.drawable_sprites)                  
                self.active_hits.empty()
            #endif
            
            # activating strike's hit objects
            self.strike_index = index
            strk = self.strikes[index]
            if len(strk) > 0:
                
                self.active_hits.add(strk.hits)                
                # adding hit objects to game object drawable sprites
                self.parent_object.drawable_group.add(strk.drawable_sprites)  
                # add strike range sprite            
                self.parent_object.add_range_sprite(strk.range_sprite)
            #endif
            
        else:
            return False
        #endif
        
        return True
    
    """
        This method is meant to be called when collisions with other game objects are reported
    """        
    def check_hits(self,game_object):
        
        hits = pygame.sprite.spritecollide(game_object, self.active_hits, False,pygame.sprite.collide_mask)
        for hit in iter(hits):
            hit.kill()
        #end


"""
Convenience class for handling multiple attacks that belong to a sequence (combo)
"""   
class AttackGroup(object):
    
    def __init__(self,game_object,attacks):
        
        self.__game_object__ = game_object
        self.__attacks__ = attacks
        self.__attack_index__ = 0
        self.__active_attack__ = None
        
        self.reset()
        
    def reset(self):
        
        # cleanup
        if self.__active_attack__ != None:
            self.__active_attack__.deactivate()
        #endif
        self.__active_attack__ = None        
        self.__attack_index__ = -1
            
    
    def select_next_attack(self):
        
        #deactivating current attack
        if self.__active_attack__ != None:
            self.__active_attack__.deactivate()
        #endif
        
        self.__attack_index__+=1
        if self.__attack_index__ < len(self.__attacks__):
            self.__active_attack__ = self.__attacks__[self.__attack_index__]
            self.__active_attack__.activate()
        #endif
        
    def len(self):
        return len(self.__attacks__)    
  
    def update_active_attack(self):
        """
            Sets the attack frame (strike) to the animation frame corresponding to this attack
        """          
        if self.__active_attack__ != None:
            return self.__active__attack__.select_strike(self.__game_object__.animation_frame_index)
        else:
            return False
        #endif
    
    @property
    def active_attack(self):
        return self.__active_attack__
    
    def active_index(self):
        return self.__attacks__.index(self.__active_attack__)

        
        
        
        
 
        
    
        
        
        
        
        
        

                                       
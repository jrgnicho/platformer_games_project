import pygame
from simple_platformer.players import Player

class AnimatedPlayer(Player):
    
    # action keys
    WALK_ACTION = 1
    STAND_ACTION = 2
    JUMP_ASCEND_ACTION = 3
    JUMP_MIDAIR_ACTION = 4
    JUMP_LAND_ACTION = 5
    JUMP_ATTACK_ACTION = 6
    
    # animation modes
    ANIMATION_MODE_CYCLE = 1
    ANIMATION_MODE_CONSUME = 2
    
    SUPPORTED_ACTIONS = [WALK_ACTION,
        STAND_ACTION,
        JUMP_ASCEND_ACTION,
        JUMP_MIDAIR_ACTION,
        JUMP_LAND_ACTION,
        JUMP_ATTACK_ACTION]
    
    def __init__(self):
        
        # supper constructor
        Player.__init__(self)
        
        # frame management
        self.time_elapsed = 0
        self.animation_frame_index = 0
        self.current_action_key = self.STAND_ACTION        
        self.last_action_key_used = self.current_action_key
        self.action_keys_queue = [self.current_action_key]
        self.animation_sprites_right_side_dict= {}
        self.animation_sprites_left_side_dict= {}
        self.facing_right = True;
        self.animation_mode = AnimatedPlayer.ANIMATION_MODE_CONSUME
        
        # collision 
        self.collision_sprite = pygame.sprite.Sprite()
        self.collision_sprite.rect = self.rect.copy()
        
        # motion state
        self.in_midair = True
        
    def add_animation_sets(self,action_key,sprite_set_right_side,sprite_set_left_side):
        """
            Adds the SpriteSet objects for the animations for the right and left sides
            corresponding to the action_key.  The action_key argument can take on the 
            values of the AnimatedPlayer global constants:
                
                AnimatedPlayer.WALK_ACTION = 1
                AnimatedPlayer.STAND_ACTION = 2
                AnimatedPlayer.JUMP_ASCEND_ACTION = 3
                AnimatedPlayer.JUMP_MIDAIR_ACTION = 4
                AnimatedPlayer.JUMP_LAND_ACTION = 5
                AnimatedPlayer.JUMP_ATTACK_ACTION = 6
        """
        
        if AnimatedPlayer.SUPPORTED_ACTIONS.count(action_key)>0:
            self.animation_sprites_right_side_dict[action_key] = sprite_set_right_side
            self.animation_sprites_left_side_dict[action_key] = sprite_set_left_side
        else:
            print "action key %i is not supported"%(action_key)
            return False
        #endif
        
        return True
    
    def remove_last_from_queue(self):
        
        num_keys = len(self.action_keys_queue)
        
        # keeps only the first
        if num_keys>1:
            self.action_keys_queue.pop()
        
            # setting current frame
            num_keys = len(self.action_keys_queue) 
            self.current_action_key = self.action_keys_queue[num_keys-1]
            self.animation_frame_index = 0
        
    def is_key_next_in_queue(self,key):
        
        num_keys = len(self.action_keys_queue) 
        found  = False
        if num_keys > 2:
            found = self.action_keys_queue[num_keys-2] == key
        else:
            found = self.action_keys_queue[0] == key
        return found
        
    def set_current_key_in_queue(self,key):
        """
        Sets key as current key.  As a result, the current animation will 
        be interrupted and replaced by the sprite frames corresponding to key
        """   
        queue_size = len(self.action_keys_queue) 
        if queue_size == 1:
            self.action_keys_queue.append(key)
        else:
            self.action_keys_queue[queue_size-1] = key
            
        self.current_action_key = key
        self.time_elapsed = pygame.time.get_ticks()
        self.animation_frame_index = 0
        
    def set_next_key_in_queue(self,key):
        """
        Sets key as the next sprite set to be animated without interrupting the current one
        """
        if len(self.action_keys_queue) == 1:
            self.set_current_key_in_queue(key)
        else:        
            self.action_keys_queue[len(self.action_keys_queue)-1] = key
            self.action_keys_queue.append(self.current_action_key)
        
    def remove_all_from_queue(self):
        """
        Removes all the frames keys elements but the first one
        and resets all counters
        """
        
        self.action_keys_queue = [self.action_keys_queue[0]];
        self.current_action_key = self.action_keys_queue[0]
        self.animation_frame_index = 0
            
    def select_next_frame(self):
        
        sprite_set = None
        if self.facing_right:
            sprite_set = self.animation_sprites_right_side_dict[self.current_action_key]
        else:
            sprite_set = self.animation_sprites_left_side_dict[self.current_action_key]
            
        current_time = pygame.time.get_ticks()
        self.animation_frame_index = (current_time- self.time_elapsed)//sprite_set.rate_change
        
        """
        # debugging
        if self.current_action_key == AnimatedPlayer.WALK_ACTION :
            self.last_action_key_used = self.current_action_key
            print "Selected WALK_ACTION with animation_frame_index %i"%(self.animation_frame_index)
        else: 
            if self.last_action_key_used == AnimatedPlayer.WALK_ACTION:
                self.last_action_key_used = self.current_action_key
                print "Switch WALK_ACTION for frame "+ str(self.current_action_key)
        #endif
        """
            
        
        # check if current sprite set has been fully animated
        if self.animation_frame_index >= len(sprite_set.sprites):
            
            # check mode
            if self.animation_mode == AnimatedPlayer.ANIMATION_MODE_CYCLE: # cycle through current sprite set
                self.time_elapsed = current_time
            elif self.animation_mode == AnimatedPlayer.ANIMATION_MODE_CONSUME:  # discart last set and use next in queue
                self.time_elapsed = current_time              
                self.remove_last_from_queue()
            
            #self.select_next_frame()
            #return           
            
            self.image = sprite_set.sprites[len(sprite_set.sprites)-1]
        else:            
            self.image = sprite_set.sprites[self.animation_frame_index]
            
        # setting values of view rectangle equal to collision
        self.rect.x = self.collision_sprite.rect.x
        self.rect.y = self.collision_sprite.rect.y
        
        # adjusting to sprite height
        self.rect.y += (self.collision_sprite.rect.height - self.image.get_height())            
        self.rect.height = self.image.get_height()
        
        # adjusting for orientation
        if not self.facing_right:
            self.rect.x -= (self.collision_sprite.rect.width - self.image.get_width()) 
            self.rect.width = self.image.get_width()
         
    #@overloaded  
    def update(self):
        
        # prevent motion if landing
        if self.current_action_key == AnimatedPlayer.JUMP_LAND_ACTION:
            self.incr.x = 0
              
        self.apply_gravity()
        
        #self.world_pos.x += self.incr.x
        #self.world_pos.y += self.incr.y  
           
        
        # collisions and boundary checks
        self.check_collisions()
        self.check_level_bounds()
        self.check_screen_bounds()
        
        
        if not self.in_midair:
            if (self.incr.x != 0) and (self.current_action_key == AnimatedPlayer.STAND_ACTION):
                self.set_current_key_in_queue(AnimatedPlayer.WALK_ACTION)  
                #print "Updated to WALK_ACTION from STAND_ACTION"
            
            if (self.incr.x == 0) and (self.current_action_key == AnimatedPlayer.WALK_ACTION):
                self.set_current_key_in_queue(AnimatedPlayer.STAND_ACTION)
                #print "Updated to STAND_ACTION from WALK_ACTION, current queue %s"%(str(self.action_keys_queue))
                
        self.select_next_frame()
        
    #@overloaded
    def apply_gravity(self):
        
        if self.incr.y ==0: # on surface or end of jump
            self.incr.y = Player.FALL_SPEED
        else:
            self.incr.y += Player.FALL_SPEED_INCREMENT # increase fall speed            
        
        # check for platform below
        self.collision_sprite.rect.y += Player.PLATFORM_CHECK_STEP
        platforms = pygame.sprite.spritecollide(self.collision_sprite,self.level.platforms,False)
        self.collision_sprite.rect.y -= Player.PLATFORM_CHECK_STEP        
        if (not self.in_midair) and (len(platforms)==0):
            self.in_midair = True
            
            
        if self.in_midair:# and (not self.is_key_next_in_queue(AnimatedPlayer.JUMP_MIDAIR_ACTION)):
            self.set_current_key_in_queue(AnimatedPlayer.JUMP_MIDAIR_ACTION)
        #    self.set_next_key_in_queue(AnimatedPlayer.JUMP_MIDAIR_ACTION)
     
    #@overloaded       
    def move_x(self,step):        
                
        self.incr.x = step    
        
        if step != 0:
            self.facing_right = (step > 0)                   
        
    #@overloaded   
    def jump(self):
        
        # check for platform below
        self.collision_sprite.rect.y += Player.PLATFORM_CHECK_STEP
        platforms = pygame.sprite.spritecollide(self.collision_sprite,self.level.platforms,False)
        self.collision_sprite.rect.y -= Player.PLATFORM_CHECK_STEP
        
        if (len(platforms) > 0) :
            
            if self.incr.x != 0:
                self.incr.y = Player.JUMP_HIGHER_SPEED
            else: 
                self.incr.y = Player.JUMP_SPEED
                
            self.in_midair = True
            
            # updating animation queue
            self.remove_all_from_queue()
            self.set_current_key_in_queue(AnimatedPlayer.JUMP_MIDAIR_ACTION)
            self.set_current_key_in_queue(AnimatedPlayer.JUMP_ASCEND_ACTION) 
            
    def resume_jump(self):
        
        if self.in_midair:
            self.incr.y = 0 
     
    ##@overloaded      
    def check_collisions(self):        
     
        
        # find colliding platforms in the y direction        
        self.collision_sprite.rect.y -= self.incr.y # increment in screen coordinates   
        platforms = pygame.sprite.spritecollide(self.collision_sprite,self.level.platforms,False)     
        for platform in platforms:
            
            # check for vertical overlaps
            if self.incr.y < 0: # falling
                self.collision_sprite.rect.bottom = platform.rect.top # landed
                self.incr.y = 0
                
                if self.in_midair:                    
                    self.remove_all_from_queue()
                    self.set_current_key_in_queue(AnimatedPlayer.JUMP_LAND_ACTION) 
                    self.incr.x = 0 # no motion in x during landing
                                          
                self.in_midair = False
                            
            elif self.incr.y > 0 : # ascending
                self.collision_sprite.rect.top = platform.rect.bottom                
                self.incr.y = 0
                
                
                if self.current_action_key == AnimatedPlayer.JUMP_ASCEND_ACTION:
                    self.remove_all_from_queue()    
                    self.set_current_key_in_queue(AnimatedPlayer.JUMP_MIDAIR_ACTION)
                    self.set_next_key_in_queue(AnimatedPlayer.JUMP_MIDAIR_ACTION)
                
        # find colliding platforms in the x direction            
        self.collision_sprite.rect.x += self.incr.x # increment in screen coordinates 
        platforms = pygame.sprite.spritecollide(self.collision_sprite,self.level.platforms,False)     
        for platform in platforms:
                
            # check for horizontal overlaps
            if self.incr.x < 0:
                self.collision_sprite.rect.left = platform.rect.right
                #self.incr.x = 0
            elif self.incr.x > 0:                
                self.collision_sprite.rect.right = platform.rect.left                
                #self.incr.x = 0                
                #print "Collision to the right, shifted %d units"%(self.collision_sprite.rect.right)            
            
        # endfor    
            
            
            
            
        
            
    
    
import pygame

from simple_platformer.utilities import Vector2D, ScreenBounds
from simple_platformer.utilities import Colors, ScreenProperties

class AnimatableObject(pygame.sprite.Sprite):
    
    # animation modes
    ANIMATION_MODE_CYCLE = 1
    ANIMATION_MODE_CONSUME = 2
    
    def __init__(self,w = 40,h = 60):
        
        pygame.sprite.Sprite.__init__(self)
        # superclass constructor
        
        # animation frame management
        self.animation_finished = False
        self.animation_time_elapsed = 0
        self.prev_animation_frame_time = 0
        self.animation_frame_index = 0
        self.animation_set_key = 0        
        self.animation_sprites_right_side_dict= {}
        self.animation_sprites_left_side_dict= {}
        self.facing_right = True;
        self.animation_mode = AnimatedPlayer.ANIMATION_MODE_CONSUME
        
        # Graphics
        self.image = pygame.Surface([w,h])
        self.image.fill(Colors.RED)
        self.rect = self.image.get_rect()
                
        # collision 
        self.collision_sprite = pygame.sprite.Sprite()
        self.collision_sprite.rect = self.rect.copy()
        
    def add_animation_sets(self,animation_set_key,sprite_set_right_side,sprite_set_left_side):
        """
            Adds the SpriteSet objects for the animating the right and left side movement sequences. 
            The animation_set_key argument can take on the must be unique since it will be used to 
            retrieve the corresponding animation sequence during animation.
        """
    
        self.animation_sprites_right_side_dict[animation_set_key] = sprite_set_right_side
        self.animation_sprites_left_side_dict[animation_set_key] = sprite_set_left_side
        
    def set_current_animation_key(self,animation_set_key):
        """
            Replaces ongoing animation with the animation corresponding to animation set key.  If animation set is
            already selected no change will be made.
            Input:
            - animation_set_key: key to Sprite set previously added to object.
            Output:
            - True/False : True if animation_set_key has a valid sprite set in the current object. False otherwise
        """
        
        # check if already selected
        if self.animation_set_key != animation_set_key:
        
            if  self.animation_sprites_right_side_dict.has_key(animation_set_key):
                self.animation_set_key = animation_set_key;
                self.animation_frame_index = 0
                self.animation_time_elapsed = 0
                self.animation_finished = False
            else:
                False
            
            #endif
        
        #endif
        
        return True
            
    def animate_next_frame(self):
        
        sprite_set = None
        if self.facing_right:
            sprite_set = self.animation_sprites_right_side_dict[self.animation_set_key]
        else:
            sprite_set = self.animation_sprites_left_side_dict[self.animation_set_key]
            
        current_time = pygame.time.get_ticks()
        self.animation_time_elapsed = current_time - self.prev_animation_frame_time
        self.animation_frame_index = (self.animation_time_elapsed)//sprite_set.rate_change
        self.prev_animation_frame_time = current_time
        
        """
        # debugging
        if self.animation_set_key == AnimatedPlayer.WALK_ACTION :
            self.last_action_key_used = self.animation_set_key
            print "Selected WALK_ACTION with animation_frame_index %i"%(self.animation_frame_index)
        else: 
            if self.last_action_key_used == AnimatedPlayer.WALK_ACTION:
                self.last_action_key_used = self.animation_set_key
                print "Switch WALK_ACTION for frame "+ str(self.animation_set_key)
        #endif
        """
            
        
        # check if current sprite set has been fully animated
        if self.animation_frame_index >= len(sprite_set.sprites):
            
            # select last frame
            self.image = sprite_set.sprites[len(sprite_set.sprites)-1]
            
            # check mode
            if self.animation_mode == AnimatableObject.ANIMATION_MODE_CYCLE: # cycle through current sprite set
                self.animation_time_elapsed = 0
                self.animation_finished = False
                
            elif self.animation_mode == AnimatableObject.ANIMATION_MODE_CONSUME:  # discart last set and use next in queue  
                self.animation_finished = True
        else: 
            
            # select following frame           
            self.image = sprite_set.sprites[self.animation_frame_index]
            
        # setting values of view rectangle equal to collision
        self.rect.x = self.collision_sprite.rect.x
        self.rect.y = self.collision_sprite.rect.y
        
        # adjusting to sprite height
        self.rect.y += (self.collision_sprite.rect.height - self.image.get_height())            
        self.rect.height = self.image.get_height()
        
        self.rect.centerx = self.collision_sprite.rect.centerx
        self.rect.width = self.image.get_width()
        
    def move_x(self,dx):        
        self.collision_sprite.rect.centerx +=dx
        
    def move_y(self,dy):
        self.collision_sprite.rect.centery +=dy
    
    def turn_right(self,x):        
        self.facing_right = True
        self.collision_sprite.rect.x +=dx
        
    def turn_left(self,x):        
        self.facing_right = False
        self.collision_sprite.rect.x -=dx
        
    def set_bb_bottom(self,bt):        
        self.collision_sprite.rect.bottom = bt
        
    def set_bb_top(self,top):
        self.collision_sprite.rect.top = top
        
    def set_bb_left(self,left):
        self.collision_sprite.rect.left = left
        
    def set_bb_right(self,rt):
        self.collision_sprite.rect.right = rt
        
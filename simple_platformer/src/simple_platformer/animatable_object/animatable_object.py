import pygame

from simple_platformer.utilities import *

class AnimatableObject(pygame.sprite.Sprite):
    
    # animation modes
    ANIMATION_MODE_CYCLE = 1
    ANIMATION_MODE_CONSUME = 2    
    
    class Events:
    
        ANIMATION_FRAME_COMPLETED = "ANIMATION_FRAME_COMPLETED"
        ANIMATION_SEQUENCE_COMPLETED = "ANIMATION_SEQUENCE_COMPLETED"
            
    
    def __init__(self,w = 40,h = 60):
        
        # superclass constructor
        pygame.sprite.Sprite.__init__(self)
        
        
        # animation frame management
        self.animation_finished = False
        self.animation_time_elapsed = 0
        self.animation_start_time = 0
        self.animation_frame_index = 0
        self.animation_set_key = 0        
        self.animation_sprites_right_side_dict= {}
        self.animation_sprites_left_side_dict= {}
        self.facing_right = True;
        self.animation_mode = AnimatableObject.ANIMATION_MODE_CYCLE
        self.animation_selected_frames = 0 # only the frames which indices are in this list will be animated 
        self.animation_cycles_counter = 0 # number of times the current animation sequence has been cycled through
        
        # Graphics
        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self)
        self.image = pygame.Surface([w,h])
        self.image.fill(Colors.RED)
        self.rect = self.image.get_rect()
                
        # collision 
        self.collision_sprite = pygame.sprite.Sprite()
        self.collision_sprite.rect = self.rect.copy()
        
        # event handlers
        self.event_handlers = {} # dictionary of lists
        self.event_handlers[AnimatableObject.Events.ANIMATION_FRAME_COMPLETED]=[]
        self.event_handlers[AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED]=[]
        
    def add_event_handler(self,event_key,handler_cb):
        
        if self.event_handlers.has_key(event_key):
            handlers = self.event_handlers[event_key]
            handlers.append(handler_cb)
            return True
        else:
            return False
    
    def remove_event_handlers(self,event_key):
        
        if self.event_handlers.has_key(event_key):
            self.event_handlers.pop(event_key)
            return True
        else:
            return False
        
    def notify(self,event_key):
        
        for handler in self.event_handlers[event_key]:
            handler()
            
        #endfor    
        
    def add_animation_sets(self,animation_set_key,sprite_set_right_side,sprite_set_left_side):
        """
            Adds the SpriteSet objects for the animating the right and left side movement sequences. 
            The animation_set_key argument can take on the must be unique since it will be used to 
            retrieve the corresponding animation sequence during animation.
        """
    
        self.animation_sprites_right_side_dict[animation_set_key] = sprite_set_right_side
        self.animation_sprites_left_side_dict[animation_set_key] = sprite_set_left_side
        
        return True
        
    def set_current_animation_key(self,animation_set_key, selected_frames = None):
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
                self.animation_start_time = pygame.time.get_ticks()
                self.animation_finished = False
                self.animation_cycles_counter = 0
                
                # checking selected index array
                if selected_frames == None:
                    self.animation_selected_frames = range(0,len(self.animation_sprites_right_side_dict[self.animation_set_key].sprites))
                    
                else:
                    self.animation_selected_frames = selected_frames
                    
                #endif
                    
            else:
                
                print TerminalColorCodes.FAIL +  "Animation set for key %s not found"%(key)
                False
        else:
            
            # checking selected index array
            if selected_frames == None:
                self.animation_selected_frames = range(0,len(self.animation_sprites_right_side_dict[self.animation_set_key].sprites))
                
            else:
                self.animation_selected_frames = selected_frames
            
            
            #endif
        
        #endif
        
        return True
    
    def draw(self,screen):
                
        self.animate_next_frame()
        self.sprite_group.draw(screen)
        #pygame.sprite.Sprite.draw(self,screen)
            
    def animate_next_frame(self):
        
        sprite_set = None
        if self.facing_right:
            sprite_set = self.animation_sprites_right_side_dict[self.animation_set_key]
        else:
            sprite_set = self.animation_sprites_left_side_dict[self.animation_set_key]
            
        current_time = pygame.time.get_ticks()
        self.animation_time_elapsed = current_time - self.animation_start_time
        frame_index_position = (self.animation_time_elapsed)//sprite_set.rate_change
        
        
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
        if frame_index_position >= len(self.animation_selected_frames):
            
            # select last frame
            last_frame_index = self.animation_selected_frames[-1]
            self.image = sprite_set.sprites[last_frame_index]
            
            # reset animation start time
            self.animation_start_time = current_time
            
            # check mode
            if self.animation_mode == AnimatableObject.ANIMATION_MODE_CYCLE: # cycle through current sprite set
                
                self.animation_time_elapsed = 0
                self.animation_finished = False                
                
            elif self.animation_mode == AnimatableObject.ANIMATION_MODE_CONSUME:  # do not continue animating expired sequence
                self.animation_time_elapsed = 0
                self.animation_finished = True
                
            #endif
            
            #print "Notifying %s event"%(AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED)
            self.animation_cycles_counter +=1
            self.notify(AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED)
            
        else: 
            
            self.animation_frame_index = self.animation_selected_frames[frame_index_position]         
            
            # select following frame           
            self.image = sprite_set.sprites[self.animation_frame_index]
            
            self.notify(AnimatableObject.Events.ANIMATION_FRAME_COMPLETED)
            
        #endif 
            
        # setting values of view rectangle equal to collision
        self.rect.x = self.collision_sprite.rect.x
        self.rect.y = self.collision_sprite.rect.y
        
        # adjusting to sprite height
        self.rect.y += (self.collision_sprite.rect.height - self.image.get_height())            
        self.rect.height = self.image.get_height()
        
        self.rect.centerx = self.collision_sprite.rect.centerx
        self.rect.width = self.image.get_width()       
        
        
        #self.print_current_animation_details("RUN")
        
    def print_current_animation_details(self, action_key):
        
        if action_key == self.animation_set_key:
        
            print "Animation key: %s, frame index: %i, selected frames: %s"%(
                                                                             self.animation_set_key,
                                                                             self.animation_frame_index,
                                                                             str(self.animation_selected_frames))
        
    def animation_set_progress_percentage(self):
        
        #sprite_set = self.animation_sprites_right_side_dict[self.animation_set_key]
        return float(self.animation_frame_index)/float(
            len(self.animation_selected_frames))
        
    def move_x(self,dx):        
        self.collision_sprite.rect.centerx +=dx
        
    def move_y(self,dy):
        self.collision_sprite.rect.centery +=dy
    
    def face_right(self):        
        self.facing_right = True
        
    def face_left(self):        
        self.facing_right = False
        
    def set_bb_bottom(self,bt):        
        self.collision_sprite.rect.bottom = bt
        
    def set_bb_top(self,top):
        self.collision_sprite.rect.top = top
        
    def set_bb_left(self,left):
        self.collision_sprite.rect.left = left
        
    def set_bb_right(self,rt):
        self.collision_sprite.rect.right = rt
        
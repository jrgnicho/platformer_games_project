import pygame

from simple_platformer.utilities import *
from simple_platformer.game_object import GameObject

class AnimatableObject(GameObject):
    
    class ActionKeys:
        ANIMATION_FRAME_ENTERED = 'ANIMATION_FRAME_ENTERED'
        ANIMATION_SEQUENCE_COMPLETED = 'ANIMATION_SEQUENCE_COMPLETED'
    
    # animation modes
    ANIMATION_MODE_CYCLE = 1
    ANIMATION_MODE_CONSUME = 2    
    
    class Events:
    
        ANIMATION_FRAME_COMPLETED = pygame.USEREVENT + 1
        ANIMATION_SEQUENCE_COMPLETED = pygame.USEREVENT + 2            
        EVENTS_LIST = [ANIMATION_FRAME_COMPLETED,ANIMATION_SEQUENCE_COMPLETED]   
        
            
    
    def __init__(self,w = 40,h = 60,parent_object = None):
        
        # superclass constructor
        GameObject.__init__(self,0,0,w,h,parent_object)
        
        
        # animation frame management
        self.animation_finished = False
        self.animation_time_elapsed = 0
        self.animation_start_time = 0
        self.animation_frame_index = 0
        self.animation_set_key = 0        
        self.animation_images_right_side_dict= {}
        self.animation_images_left_side_dict= {}
        self.facing_right = True;
        self.animation_mode = AnimatableObject.ANIMATION_MODE_CYCLE
        self.animation_selected_frames = [] # 0 # only the frames which indices are in this list will be animated 
        self.animation_cycles_counter = 0 # number of times the current animation sequence has been cycled through
        self.animation_keys_queue = []
        
        # event handlers
        self.event_queue = [AnimatableObject.Events.ANIMATION_FRAME_COMPLETED]
        self.event_handlers = {} # dictionary with event keys
        self.event_handlers[AnimatableObject.Events.ANIMATION_FRAME_COMPLETED]={} # dictionary with (game_object, event) pairs
        self.event_handlers[AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED]={}
        
    def add_event_handler(self,event_key,game_obj,handler_cb):
        
        if self.event_handlers.has_key(event_key):
            
            event_dict = self.event_handlers[event_key]
            
            # create event and save
            event = pygame.event.Event(event_key,{'notify':handler_cb})
            event_dict[game_obj] = event
            return True
        else:
            print 'Event %s is not a supported animation event'%(event_key)
            return False
        
    def remove_event_handler(self,event_key,game_obj):
        
        if self.event_handlers.has_key(event_key):
            event_dict = self.event_handlers[event_key]
            
            if event_dict.has(game_obj):
                del event_dict[game_obj]
            #endif
        #endif
        
    
    def remove_all_event_handlers(self,event_key):
        
        if self.event_handlers.has_key(event_key):
            del self.event_handlers[event_key]
            return True
        else:
            return False
        
    def post_events(self,event_key):
        
        event_dict = self.event_handlers[event_key]
        for event in event_dict.values():
            pygame.event.post(event)          
        #endfor    
        
    def add_animation_sets(self,animation_set_key,sprite_set_right_side,sprite_set_left_side):
        """
            Adds the SpriteSet objects for the animating the right and left side movement sequences. 
            The animation_set_key argument can take on the must be unique since it will be used to 
            retrieve the corresponding animation sequence during animation.
        """
    
        self.animation_images_right_side_dict[animation_set_key] = sprite_set_right_side
        self.animation_images_left_side_dict[animation_set_key] = sprite_set_left_side
        
        return True
    
    def queue_animation_keys(self,keys):
        
        for k in keys:
            if  self.animation_images_right_side_dict.has_key(k):
                self.animation_keys_queue.append(k)
            else:
                print "ERROR: animation key %s can not be queued"%(k)
            #endif
        #endfor
    
    def select_next_queued(self):
        
        if len(self.animation_keys_queue) > 0:
            key = self.animation_keys_queue.pop(0)
            self.set_current_animation_key(key)
        else:
            return False
        #endif
        
        return True
    
    def clear_queue(self):
        self.animation_keys_queue = []
        
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
        
            if  self.animation_images_right_side_dict.has_key(animation_set_key):
                self.animation_set_key = animation_set_key;
                self.animation_frame_index = 0
                self.animation_time_elapsed = 0
                self.animation_start_time = pygame.time.get_ticks()
                self.animation_finished = False
                self.animation_cycles_counter = 0
                
                # checking selected index array
                if selected_frames == None:
                    self.animation_selected_frames = range(0,len(self.animation_images_right_side_dict[self.animation_set_key].sprites))
                    
                else:
                    self.animation_selected_frames = selected_frames                    
                #endif               

                    
            else:
                
                #print TerminalColorCodes.FAIL +  "Animation set for key %s not found"%(animation_set_key)
                print "ERROR: " +  "Animation set for key %s not found"%(animation_set_key)
                False
        else:
            
            # checking selected index array
            if selected_frames == None:
                self.animation_selected_frames = range(0,len(self.animation_images_right_side_dict[self.animation_set_key].sprites))
                
            else:
                self.animation_selected_frames = selected_frames
            
            #endif
        
        #endif
        
        return True
    
    def draw(self,screen):
                
        self.drawable_group.draw(screen)
        
    def update(self):
        
        self.update_animation_frame()
        for evnt in iter(self.event_queue):        
            self.post_events(evnt)
        #endfor
        self.event_queue = []
            
    def update_animation_frame(self):
        
        sprite_set = None
        if self.facing_right:
            sprite_set = self.animation_images_right_side_dict[self.animation_set_key]
        else:
            sprite_set = self.animation_images_left_side_dict[self.animation_set_key]
            
        current_time = pygame.time.get_ticks()
        self.animation_time_elapsed = current_time - self.animation_start_time
        frame_index_position = (self.animation_time_elapsed)//sprite_set.rate_change
            
        
        # check if current sprite set has been fully animated
        if frame_index_position >= len(self.animation_selected_frames):
            
            # select last frame
            last_frame_index = self.animation_selected_frames[-1]
            #self.drawable_sprite.image = sprite_set.sprites[last_frame_index].image
            self.drawable_sprite.set_from(sprite_set.sprites[last_frame_index])
            
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
            self.event_queue.append( AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED)
            
        else: 
            
            self.animation_frame_index = self.animation_selected_frames[frame_index_position]         
            
            # select following frame           
            self.drawable_sprite.set_from(sprite_set.sprites[self.animation_frame_index])
            self.event_queue.append(AnimatableObject.Events.ANIMATION_FRAME_COMPLETED)
            
        #endif             
        
        self.drawable_sprite.bottom = self.screen_bottom 
        self.drawable_sprite.centerx = self.screen_centerx     
        
        
        
    def print_current_animation_details(self, animation_key):
        
        if animation_key == self.animation_set_key:
        
            print "Animation key: %s, frame index: %i, selected frames: %s"%(
                                                                             self.animation_set_key,
                                                                             self.animation_frame_index,
                                                                             str(self.animation_selected_frames))
        
    def get_animation_progress_percentage(self):
        
        #sprite_set = self.animation_images_right_side_dict[self.animation_set_key]
        if self.animation_selected_frames.count(self.animation_frame_index) == 0:
            return 0
        
        index = self.animation_selected_frames.index(self.animation_frame_index)
        return float(index+1)/float(
            len(self.animation_selected_frames))

        
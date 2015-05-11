import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import StateMachine
from simple_platformer.game_state_machine import SubStateMachine
from simple_platformer.game_state_machine import StateMachineActionKeys
from simple_platformer.game_object import *
from combat_platformer.player.action_keys import PlayerActionKeys
from combat_platformer.attack import *



class AttackState(SubStateMachine):
    
    DIRECTION_CHANGE_THRESHOLD = 0.4
    NEXT_ATTACK_THRESHOLD = 0.3
    
    class StateKeys(object):
        
        ACTIVE = 'ATTACK_ACTIVE'
        CONTINUE = 'ATTACK_CONTINUE'
    
    class BaseAttackState(State):
        """
        BaseAttackState(game_object,attack_group,interrupt_indices)
            game_object: Object that spawns the attack
            attack_group : AttackGroup object containing the attacks to be managed by this state
            interrupt_indices: Dictionary of key and indices pairs where each key is use to look up an Attack object in the attack_group
                                argument, the value indicates the animation frame when the attack ends.
                                Defaults to [-1, ..., -1] same size as the attacks array.  It must have a size equal to the number of 
                                attacks in the 'attacks' argument
        """
        
        def __init__(self,key,game_object,attack_group, interrupt_indices = None):            
            State.__init__(self,key)
            self.__game_object__ = game_object
            self.__attack_group__ = attack_group
            self.facing_right = True
            
            # Defaults to the last frame (no early interruptions) 
            if interrupt_indices == None:
                interrupt_indices = {}
                keys = attack_group.attack_keys
                print str(keys)
                for k in keys:
                    at = attack_group.get(k)
                    interrupt_indices[k] = at.strikes_count() - 1
                #endfor
            #endif  
            self.__interrupt_indices__ = interrupt_indices    
            
            self.add_action(PlayerActionKeys.MOVE_LEFT,lambda : self.set_direction(False))
            self.add_action(PlayerActionKeys.MOVE_RIGHT,lambda : self.set_direction(True))    
            
        def set_direction(self,facing_right):
            if (self.__game_object__.animation_frame_index 
                > AttackState.DIRECTION_CHANGE_THRESHOLD*self.__attack_group__.active_attack.strikes_count()):
                self.facing_right = facing_right
                        
        def reset(self):
            self.facing_right = self.__game_object__.facing_right
            self.__attack_group__.reset()          
        
    class ActiveState(BaseAttackState):
        """
        ActiveState(game_object,attack_group,interrupt_indices)
        This state updates the attack so that the game_object animation and the corresponding attack strikes are in sync.
        """
        
        def __init__(self,game_object,attack_group, interrupt_indices = None): 
            AttackState.BaseAttackState.__init__(self,AttackState.StateKeys.ACTIVE,game_object,attack_group,interrupt_indices)
            
            # Animation image frame entered
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_FRAME_COMPLETED,
                lambda : self.frame_entered_callback())
            
            # Attack button(s) pressed
            self.add_action(PlayerActionKeys.ATTACK,
                lambda : self.attack_action_callback())
            
            # Exit attack when animation for the active state ends
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_SEQUENCE_COMPLETED,
                lambda : self.sequence_completed_callback())
            
        def enter(self):            
            self.__game_object__.select_next_queued() # Queueing the animations in the game objects makes it possible to track the queue
                                                      # without having to mantain and sync multiple queue arrays
            self.__attack_group__.select_attack(self.__game_object__.animation_set_key)
            
        def exit(self):
            self.__game_object__.facing_right = self.facing_right
            
        def frame_entered_callback(self):          
            self.__attack_group__.update_active_attack()

        def attack_action_callback(self):  
            # Delegate the management of the attack to the Continue state if the NEXT_ATTACK_TRESHOLD has been exceeded          
            if (self.__game_object__.animation_frame_index 
                > AttackState.NEXT_ATTACK_THRESHOLD*self.__attack_group__.active_attack.strikes_count()):
                StateMachine.post_action_event(self.__game_object__,
                               AttackStateActionKeys.CONTINUE_NEXT,
                                StateMachine.Events.SUBMACHINE_ACTION)
            #endif  
            
        def sequence_completed_callback(self):
            
            # Should quit the containing sub machine
            StateMachine.post_action_event(self.__game_object__,
                           AttackStateActionKeys.SEQUENCE_COMPLETED,
                            StateMachine.Events.SUBMACHINE_ACTION)     
        
            
    class ContinueState(BaseAttackState):
        
        def __init__(self,game_object,attack_group, interrupt_indices = None): 
            AttackState.BaseAttackState.__init__(self,AttackState.StateKeys.CONTINUE,game_object,attack_group,interrupt_indices)
            
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_FRAME_COMPLETED,
                lambda : self.frame_entered_callback())
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_SEQUENCE_COMPLETED,
                lambda : self.sequence_completed_callback())
            
        def enter(self):
            pass
        
        def exit(self):
            pass
            
        def frame_entered_callback(self):            
            key = self.__attack_group__.active_key
            if self.__interrupt_indices__[key] == self.__game_object__.animation_frame_index:
                
                # Send to the Active State in order to start the next attack if the animation for the current attack has ended.  
                StateMachine.post_action_event(self.__game_object__,
                               AttackStateActionKeys.ENTER_NEXT,
                                StateMachine.Events.SUBMACHINE_ACTION)
            else:
                
                # updates the active attack
                self.__attack_group__.update_active_attack()
            #endif
            
        def sequence_completed_callback(self):
            
            # Send to the Active State in order to start the next attack if the animation for the current attack has ended. 
            if len(self.__game_object__.animation_keys_queue) == 0:
                # Exit submachine when last animation sequence has been completed
                StateMachine.post_action_event(self.__game_object__,
                               AttackStateActionKeys.SEQUENCE_COMPLETED,
                                StateMachine.Events.SUBMACHINE_ACTION)    
            #endif                                   

    
    def __init__(self,key,game_object,attack_keys):
        
        SubStateMachine.__init__(self,key,game_object)
        self.__game_object__ = game_object
        self.__attacks__ = None
        self.__attack_group__ = None
        self.__attack_keys__ = attack_keys
        
        # state place holders
        self.active_state = None
        self.continue_state = None
        
    def enter(self):        
        
        self.__game_object__.add_event_handler(AnimatableObject.Events.ANIMATION_FRAME_COMPLETED,self,
                               lambda: self.execute(AnimatableObject.ActionKeys.ANIMATION_FRAME_COMPLETED))
        
        self.__game_object__.set_horizontal_speed(0)
        self.__game_object__.queue_animation_keys(self.__attack_keys__)
                
        self.active_state.reset()
        self.continue_state.reset()
        
        SubStateMachine.enter(self)
        
    def exit(self):
        
        self.__game_object__.remove_event_handler(AnimatableObject.Events.ANIMATION_FRAME_COMPLETED,self)
        self.__game_object__.clear_queue()
        
        SubStateMachine.exit(self)
        
    def setup(self,assets):
        
        # create attack group
        self.__attack_group__ = AttackGroup(self.__game_object__, {})
        
        # creating attacks
        for k in self.__attack_keys__:
            
            if assets.collision_sprite_loader.has_set(k) and assets.animation_sprite_loader.has_set(k):
                a = Attack(self.__game_object__, (assets.collision_sprite_loader.sprite_sets[k],
                                                  assets.collision_sprite_loader.sprite_sets[k].invert_set()))
                self.__attack_group__.add(k,a)
                self.__game_object__.add_animation_sets(k,assets.animation_sprite_loader.sprite_sets[k],
                                                assets.animation_sprite_loader.sprite_sets[k].invert_set())
            else:
                print "ERROR: Collision sprite set %s was not found"%(k)
                return False
            #endif
        #endfor        
        
        # create states
        self.active_state = AttackState.ActiveState(self.__game_object__,self.__attack_group__)
        self.continue_state = AttackState.ContinueState(self.__game_object__,self.__attack_group__)
        
        self.create_transition_rules()
        
        return True
    
    def create_transition_rules(self):        
                
        # transitions
        self.add_transition(self.start_state, StateMachineActionKeys.SUBMACHINE_START, self.active_state.key)
        self.add_transition(self.active_state, AttackStateActionKeys.CONTINUE_NEXT, self.continue_state.key)
        self.add_transition(self.continue_state, AttackStateActionKeys.ENTER_NEXT, self.active_state.key)
        self.add_transition(self.active_state, AttackStateActionKeys.SEQUENCE_COMPLETED, self.stop_state.key)
        self.add_transition(self.continue_state, AttackStateActionKeys.SEQUENCE_COMPLETED, self.stop_state.key)
        

        
    
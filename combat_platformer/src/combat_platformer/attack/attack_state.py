import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import SubStateMachine
from simple_platformer.game_object import *
from combat_platformer.player import PlayerActionKeys
from combat_platformer.attack import *



class AttackState(SubStateMachine):
    
    class StateKeys(object):
        
        ACTIVE = 'ATTACK_ACTIVE'
        CONTINUE = 'ATTACK_CONTINUE'
    
    class BaseAttackState(State):
        """
        BaseAttackState(game_object,attacks,interrupt_indices)
            game_object: Object that spawns the attack
            attacks : Array of attack objects
            interrupt_indices: Array of indices at which each attack frame will end and continue onto the next attack.
                Defaults to [-1, ..., -1] same size as the attacks array.
        """
        
        def __init__(self,game_object,attack_group, interrupt_indices = None):            
            State.__init__(self,AttackState.StateKeys.ACTIVE)
            self.__game_object__ = game_object
            self.__attack_group__ = attack_group
            
            if interrupt_indices == None:
                interrupt_indices = []
                for at in attacks:
                    interrupt_indices.append(at.strike_count() - 1)
                #endfor
            #endif            
            
            self.__interrupt_indices__ = interrupt_indices            
            
        def reset(self):
            self.__attack_group__.reset()          
        
    class ActiveState(State):
        
        def __init__(self,game_object,attack_group, interrupt_indices = None): 
            AttackState.BaseAttackState.__init__(self,game_object,attacks,interrupt_indices)
            
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_FRAME_ENTERED,
                lambda : self.frame_entered_callback())
            self.add_action(PlayerActionKeys.ATTACK,
                lambda : self.attack_action_callback())
            
        def enter(self):
            self.__game_object__.select_next_queued()
            self.__attack_group__.select_next_attack()
            
        def frame_entered_callback(self):            
            self.__attack_group__.update_active_attack()

        def attack_action_callback(self):            
            if self.__game_object__.animation_frame_index> 0.5*self.__attack_group__.active_attack.get_strike_count():
                StateMachine.post_action_event(self.__game_object__,
                               AttackStateActionKeys.QUEUE_NEXT,
                                StateMachine.Events.SUBMACHINE_ACTION)
            #endif       
        
            
    class ContinueState(State):
        
        def __init__(self,game_object,attack_group, interrupt_indices = None): 
            AttackState.BaseAttackState.__init__(self,game_object,attacks,interrupt_indices)
            
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_FRAME_ENTERED,
                lambda : self.frame_entered_callback())
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_SEQUENCE_COMPLETED,
                lambda : self.sequence_completed_callback())
            self.add_action(PlayerActionKeys.ATTACK,
                lambda : self.attack_action_callback())
            
        def frame_entered_callback(self):            
            active_index = self.__attack_group__.active_index()
            if self.__interrupt_indices__[active_index] == self.__game_object__.animation_frame_index:
                StateMachine.post_action_event(self.__game_object__,
                               AttackStateActionKeys.ENTER_NEXT,
                                StateMachine.Events.SUBMACHINE_ACTION)
            else:
                self.__attack_group__.update_active_attack()
            #endif
            
        def sequence_completed_callback(self):
            
            if len(self.__attack_group__) > (self.__attack_group__.active_index()+1):
                StateMachine.post_action_event(self.__game_object__,
                               AttackStateActionKeys.ENTER_NEXT,
                                StateMachine.Events.SUBMACHINE_ACTION)  
            else:
                StateMachine.post_action_event(self.__game_object__,
                               AttackStateActionKeys.SEQUENCE_COMPLETED,
                                StateMachine.Events.SUBMACHINE_ACTION)    
            #endif                                   

    
    def __init__(self,key,game_object,attack_keys):
        
        SubStateMachine.__init__(self,key)
        self.__game_object__ = game_object
        self.__attacks__ = None
        self.__attack_group__ = None
        self.__attack_keys__ = attack_keys
        
        # state place holders
        self.active_state = None
        self.continue_state = None
        
    def enter(self):        
        self.__game_object__.queue_animation_keys(self.__attack_keys)
        
    def exit(self):
        self.__game_object__.clear_queue()
        
    def setup(self,assets):
        
        # creating attacks
        attacks = []
        for k in self.__attack_keys:
            
            if assets.attack_images.has_key(k):
                a = Attack(self.__game_object__, assets.attack_images[k])
                attacks.append(a)
            else:
                print "ERROR: attack image for key %s was not found"%(k)
                return False
            #endif
        #endfor
        
        # create attack group
        self.__attack_group__ = AttackGroup(self.__game_object__, attacks)
        
        # create states
        self.active_state = AttackState.ActiveState(self.__game_object__,self.__attack_group__)
        self.continue_state = AttackState.ContinueState(self.__game_object__,self.__attack_group__)
        
        self.create_transition_rules()
        
        return True
    
    def create_transition_rules(self):        
                
        # transitions
        self.add_transition(self.start_state, StateMachineActionKeys.SUBMACHINE_START, self.active_state.key)
        self.add_transition(self.active_state, AttackStateActionKeys.QUEUE_NEXT, self.continue_state.key)
        self.add_transition(self.continue_state, AttackStateActionKeys.ENTER_NEXT, self.active_state.key)
        self.add_transition(self.continue_state, AttackStateActionKeys.SEQUENCE_COMPLETED, self.stop_state.key)
        

        
    
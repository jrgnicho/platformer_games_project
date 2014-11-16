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
    
    class ActiveState(State):
        
        def __init__(self,game_object):            
            State.__init__(self,AttackState.StateKeys.ACTIVE)
            self.__game_object__ = game_object
            self.__attacks__ = None
            self.__attack_index__ = 0
            self.__active_attack__ = None
            
            # transition members
            self.continue_next = False
            self.finished = False
            
            self.add_action(AnimatableObject.ActionKeys.ANIMATION_FRAME_ENTERED,
                            lambda : self.update_attack())
            
        def reset(self):
            self.__attack_index__ = 0
            self.__active_attack__ = None
            
        @attacks.setter
        def attacks(self,attacks):
            self.__attacks__ = attacks
            
        def enter(self):
            if self.__attack_index__ < len(self.__attacks__):
                self.__active_attack__ = self.__attacks__[self.__attack_index__]
                self.__active_attack__.activate()
        
        def exit(self):
            self.__attack_index__+=1
            self.__active_attack__.deactivate()
            
            if self.__attack_index__ >= len(self.__attacks__):
                self.__attack_index__ = 0
            #endif
            
        def update_attack(self):
            if self.__active_attack__:
                self.__active__attack__.select_strike(self.__game_object__.animation_frame_index)
            #endif
            
        def queue_attack(self):            
            if self.__game_object__.animation_frame_index> 0.5*self.__active_attack__.get_strike_count():
                self.continue_next = True
            #endif       
        
            
    class ContinueState(State):
        
        def __init__(self,game_object):            
            State.__init__(self,AttackState.StateKeys.CONTINUE)
            self.__game_object__ = game_object
            self.__attacks__ = None
            
        @attacks.setter
        def attacks(self,attacks):
            self.__attacks__
            
    
    def __init__(self,key,game_object):
        
        SubStateMachine.__init__(self,key)
        self.__game_object__ = game_object
        self.__attacks__ = None
        
        # creating states
        self.__activate_state = AttackState.ActiveState(self.__game_object__)
        self.__continue_state = AttackState.ContinueState(self.__game_object__)
        
    
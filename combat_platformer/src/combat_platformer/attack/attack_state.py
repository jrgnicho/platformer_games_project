import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import SubStateMachine
from simple_platformer.game_object import *
from combat_platformer.attack import *



class AttackState(SubStateMachine):
    
    class StateKeys(object):
        
        ACTIVATE = 'ATTACK/ACTIVATE'
        CONTINUE = 'ATTACK/CONTINUE'
    
    class ActivateState(State):
        
        def __init__(self,game_object):            
            State.__init__(self,AttackState.StateKeys.ACTIVATE)
            self.__game_object__ = game_object
            self.__attacks__ = None
            
            
    class ContinueState(State):
        
        def __init__(self,game_object):            
            State.__init__(self,AttackState.StateKeys.CONTINUE)
            self.__game_object__ = game_object
            self.__attacks__ = None
            
    
    def __init__(self,key,game_object):
        
        SubStateMachine.__init__(self,key)
        self.__game_object__ = game_object
        self.__attacks__ = None
        
        # creating states
        self.__activate_state = AttackState.ActivateState(self.__game_object__)
        self.__continue_state = AttackState.ContinueState(self.__game_object__)
        
    
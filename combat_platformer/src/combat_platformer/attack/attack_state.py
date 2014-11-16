import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import SubStateMachine
from simple_platformer.game_object import *
from combat_platformer.attack import *

class AttackState(SubStateMachine):
    
    def __init__(self,key,game_object,):
        
        SubStateMachine.__init__(self,key)
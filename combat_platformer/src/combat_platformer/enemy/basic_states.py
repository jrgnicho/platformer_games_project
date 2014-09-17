import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import SubStateMachine

class StateKeys(object):
    
    PATROL = 'PATROL'
    ALERT='ALERT'
    CHASE='CHASE'
    WALK = 'WALK'
    JUMP='JUMP'
    NAP='NAP'
    
    
class PatrolState(SubStateMachine):
    
    def __init__(self,parent_sm):
        
        SubStateMachine.__init__(self,StateKeys.PATROL ,parent_sm)
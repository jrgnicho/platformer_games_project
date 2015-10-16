from physics_platformer.game_objects import CharacterObject
from physics_plaformer.character.character_states import CharacterStateKeys
from physics_platformer.character.character_states import *
from physics_platformer.character import CharacterStateMachine

class Character(CharacterObject):
  
  def __init__(self,character_info):
    CharacterObject.__init__(self.character_info)
    
    self.controller_ = CharacterStateMachine()    
    
  def setup(self):
    
    # creating default states
    standing_state = StandingState(self, self.controller_)
    running_state = RunningState(self,self.controller_)
    takeoff_state = TakeoffState(self,self.controller_)
    jump_state = JumpState(self,self.controller_)
    fall_state = FallState(self,self.controller_)
    land_state = LandState(self,self.controller_)
    
    self.controller_.addState(standing_state.key)
    self.controller_.addState(running_state.key)
    self.controller_.addState(takeoff_state.key)
    self.controller_.addState(jump_state.key)
    self.controller_.addState(fall_state.key)
    self.controller_.addState(land_state.key)
    
    self.controller_.setup()
    
    return True
    
  def execute(self,action):
    self.controller_.execute(action)
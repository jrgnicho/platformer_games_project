from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func
from platformer_core.game_actions import *

class MotionCommander(object):
  
  def __init__(self, character):
    self.character_ = character
    self.move_execution_seq_ = Sequence()
    
  def moveRight(self):    
    self.move_execution_seq_.finish()
    self.move_execution_seq_.clearIntervals()
    self.move_execution_seq_ = Sequence()
    finterv = Func(lambda : self.character_.execute(CharacterActions.MOVE_RIGHT))
    self.move_execution_seq_.append(finterv)
    self.move_execution_seq_.loop()
  
  def moveLeft(self):
    self.move_execution_seq_.finish()
    self.move_execution_seq_.clearIntervals()
    self.move_execution_seq_ = Sequence()
    finterv = Func(lambda : self.character_.execute(CharacterActions.MOVE_LEFT))
    self.move_execution_seq_.append(finterv)
    self.move_execution_seq_.loop()
  
  def stop(self):
    self.move_execution_seq_.finish()
    self.move_execution_seq_.clearIntervals()
    self.move_execution_seq_ = Sequence()
    finterv = Func(lambda :self.character_.execute(CharacterActions.MOVE_NONE))
    self.move_execution_seq_.append(finterv)
    self.move_execution_seq_.loop()
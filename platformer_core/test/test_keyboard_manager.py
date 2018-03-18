#!/usr/bin/env python3
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpFunc
from direct.task.TaskManagerGlobal import taskMgr
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.controls.InputState import InputState
from panda3d.core import ClockObject

from platformer_core.input import Move
from platformer_core.input import KeyboardButtons
from platformer_core.input import KeyboardController
import sys
import logging

class TestKeyboardController(ShowBase):
  
  def __init__(self):    
    ShowBase.__init__(self)
    
    
    self.clock_ = ClockObject()
    self.setupInput()    
    taskMgr.add(self.update,"update")
    
  def update(self,task):
    self.clock_.tick()
    dt = self.clock_.getDt()    
    self.input_manager_.update(dt)
    return task.cont
  
  def exitCallback(self):
    sys.exit(0)
  
  def setupInput(self):
    
    self.input_state_ = InputState()
    
    # Creating button map
    button_map = {'a' : KeyboardButtons.KEY_A , 'q' : KeyboardButtons.KEY_Q,
                  's' : KeyboardButtons.KEY_S , 'w' : KeyboardButtons.KEY_W,
                  'd' : KeyboardButtons.KEY_D , 'e' : KeyboardButtons.KEY_E,
                  'x' : KeyboardButtons.KEY_X , 'c' : KeyboardButtons.KEY_C,
                  'space' : KeyboardButtons.KEY_SPACE , 'shift' : KeyboardButtons.KEY_SHIFT,
                  'escape' : KeyboardButtons.KEY_ESC}
  
    
    self.input_manager_ = KeyboardController(self.input_state_, button_map)
    
    # Creating directional moves
    self.input_manager_.addMove(Move('UP',[KeyboardButtons.DPAD_UP],True))
    self.input_manager_.addMove(Move('DOWN',[KeyboardButtons.DPAD_DOWN],True))
    self.input_manager_.addMove(Move('LEFT',[KeyboardButtons.DPAD_LEFT],True))
    self.input_manager_.addMove(Move('RIGHT',[KeyboardButtons.DPAD_RIGHT],True))
    self.input_manager_.addMove(Move('DOWN_RIGHT',[KeyboardButtons.DPAD_DOWNRIGHT],True))
    self.input_manager_.addMove(Move('DOWN_LEFT',[KeyboardButtons.DPAD_DOWNLEFT],True))
    self.input_manager_.addMove(Move('UP_LEFT',[KeyboardButtons.DPAD_UPLEFT],True))
    self.input_manager_.addMove(Move('UP_RIGHT',[KeyboardButtons.DPAD_UPRIGHT],True))
    
    # Creating action moves
    self.input_manager_.addMove(Move('JUMP',[KeyboardButtons.KEY_A],True))
    self.input_manager_.addMove(Move('DASH',[KeyboardButtons.KEY_S],True))
    self.input_manager_.addMove(Move('LIGHT ATTACK',[KeyboardButtons.KEY_D],True))
    self.input_manager_.addMove(Move('FUERTE ATTACK',[KeyboardButtons.KEY_E],True))
    
    # released moves
    self.input_manager_.addMove(Move('RELEASE_UP',[KeyboardButtons.DPAD_UP],True),False)
    self.input_manager_.addMove(Move('RELEASE_DOWN',[KeyboardButtons.DPAD_DOWN],True),False)
    self.input_manager_.addMove(Move('RELEASE_LEFT',[KeyboardButtons.DPAD_LEFT],True),False)
    self.input_manager_.addMove(Move('RELEASE_RIGHT',[KeyboardButtons.DPAD_RIGHT],True),False)
    self.input_manager_.addMove(Move('RELEASE FUERTE ATTACK',[KeyboardButtons.KEY_E],True),False)
    self.input_manager_.addMove(Move('RELEASE LIGHT ATTACK',[KeyboardButtons.KEY_D],True),False)
    
    # exit
    self.input_manager_.addMove(Move('SPECIAL ATTACK',[KeyboardButtons.KEY_D, KeyboardButtons.KEY_E],False,lambda : self.exitCallback()))
    
    # Creating special moves
    self.input_manager_.addMove(Move('EXIT',[KeyboardButtons.KEY_ESC],False,lambda : self.exitCallback()))
    
    self.input_manager_.addMove(Move('RIGHT ABUKE PRO',[KeyboardButtons.DPAD_DOWN,
                                                 KeyboardButtons.DPAD_DOWNRIGHT,
                                                 KeyboardButtons.DPAD_RIGHT,
                                                 KeyboardButtons.DPAD_RIGHT | KeyboardButtons.KEY_D],False,
                                        lambda : sys.stdout.write("-----> RIGHT ABUKE\n")))
    
    self.input_manager_.addMove(Move('LEFT ABUKE PRO',[KeyboardButtons.DPAD_DOWN,
                                                 KeyboardButtons.DPAD_DOWNLEFT,
                                                 KeyboardButtons.DPAD_LEFT,
                                                 KeyboardButtons.DPAD_LEFT | KeyboardButtons.KEY_D],False,
                                        lambda : sys.stdout.write("-----> LEFT ABUKE \n")))
                                        
    
if __name__ == '__main__':
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  t = TestKeyboardController()    
  t.run()  
  
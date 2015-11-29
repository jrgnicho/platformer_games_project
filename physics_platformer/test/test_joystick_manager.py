#!/usr/bin/env python
import pygame
import sys

from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpFunc
from direct.task.TaskManagerGlobal import taskMgr
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.controls.InputState import InputState
from panda3d.core import ClockObject

from physics_platformer.input import Move
from physics_platformer.input import JoystickButtons
from physics_platformer.input import JoystickController
import sys
import logging

class TestJoystickController(ShowBase):
  
  def __init__(self):    
    ShowBase.__init__(self)
    
    
    self.clock_ = ClockObject()
    self.setupInput()    
    taskMgr.add(self.update,"update")
    
  def update(self,task):
    self.clock_.tick()
    dt = self.clock_.getDt()   
    pygame.event.get()
    self.joystick_manager_.update(dt)
    return task.cont
  
  def exitCallback(self):
    sys.exit(0)
    
    
  def setupInput(self):
        
    # Creating button map
    button_map = {0 : JoystickButtons.BUTTON_X , 3 : JoystickButtons.BUTTON_Y,
                  1 : JoystickButtons.BUTTON_A , 2 : JoystickButtons.BUTTON_B,
                  7 : JoystickButtons.TRIGGER_R1 , 5 : JoystickButtons.TRIGGER_R2,
                  6 : JoystickButtons.TRIGGER_L1 , 4 : JoystickButtons.TRIGGER_L2,
                  9 : JoystickButtons.BUTTON_START , 8 : JoystickButtons.BUTTON_SELECT,
                  10: JoystickButtons.TRIGGER_L3   , 11: JoystickButtons.TRIGGER_R3}
    

    if pygame.joystick.get_count() <=  0:
      logging.error("No Joysticks were found, exiting")
      sys.exit(-1)
      
    joystick = None
    for j in range(0,pygame.joystick.get_count()):
      joystick = pygame.joystick.Joystick(j)
      if joystick.init() and joystick.get_numbuttons() > 0:
        break;
      
    self.joystick_manager_ = JoystickController(button_map,joystick, JoystickController.JoystickAxes(),2)
    
    # Creating directional moves
    self.joystick_manager_.addMove(Move('UP',[JoystickButtons.DPAD_UP],True))
    self.joystick_manager_.addMove(Move('DOWN',[JoystickButtons.DPAD_DOWN],True))
    self.joystick_manager_.addMove(Move('LEFT',[JoystickButtons.DPAD_LEFT],True))
    self.joystick_manager_.addMove(Move('RIGHT',[JoystickButtons.DPAD_RIGHT],True))
    self.joystick_manager_.addMove(Move('DOWN_RIGHT',[JoystickButtons.DPAD_DOWNRIGHT],True))
    self.joystick_manager_.addMove(Move('DOWN_LEFT',[JoystickButtons.DPAD_DOWNLEFT],True))
    self.joystick_manager_.addMove(Move('UP_LEFT',[JoystickButtons.DPAD_UPLEFT],True))
    self.joystick_manager_.addMove(Move('UP_RIGHT',[JoystickButtons.DPAD_UPRIGHT],True))
    
    # Creating action moves
    self.joystick_manager_.addMove(Move('JUMP',[JoystickButtons.BUTTON_B],True))
    self.joystick_manager_.addMove(Move('DASH',[JoystickButtons.BUTTON_A],True))
    self.joystick_manager_.addMove(Move('LIGHT ATTACK',[JoystickButtons.BUTTON_Y],True))
    self.joystick_manager_.addMove(Move('FUERTE ATTACK',[JoystickButtons.BUTTON_X],True))
    
    # Creating release moves
    self.joystick_manager_.addMove(Move('UP_RELEASE',[JoystickButtons.DPAD_UP],True),False)
    self.joystick_manager_.addMove(Move('DOWN_RELEASE',[JoystickButtons.DPAD_DOWN],True),False)
    self.joystick_manager_.addMove(Move('LEFT_RELEASE',[JoystickButtons.DPAD_LEFT],True),False)
    self.joystick_manager_.addMove(Move('RIGHT_RELEASE',[JoystickButtons.DPAD_RIGHT],True),False)
    self.joystick_manager_.addMove(Move('JUMP_RELEASE',[JoystickButtons.BUTTON_B],True),False)
    self.joystick_manager_.addMove(Move('DASH_RELEASE',[JoystickButtons.BUTTON_A],True),False)
    self.joystick_manager_.addMove(Move('LIGHT ATTACK_RELEASE',[JoystickButtons.BUTTON_Y],True),False)
    self.joystick_manager_.addMove(Move('FUERTE ATTACK_RELEASE',[JoystickButtons.BUTTON_X],True),False)
    
    # Creating special moves
    self.joystick_manager_.addMove(Move('RIGHT ABUKE PRO',[JoystickButtons.DPAD_DOWN,
                                                 JoystickButtons.DPAD_DOWNRIGHT,
                                                 JoystickButtons.DPAD_RIGHT,
                                                 #JoystickButtons.DPAD_RIGHT | JoystickButtons.BUTTON_Y],False,
                                                 JoystickButtons.BUTTON_Y],False,
                                        lambda : sys.stdout.write("<-----> RIGHT ABUKE\n")))
    
    self.joystick_manager_.addMove(Move('LEFT ABUKE PRO',[JoystickButtons.DPAD_DOWN,
                                                 JoystickButtons.DPAD_DOWNLEFT,
                                                 JoystickButtons.DPAD_LEFT,
                                                 #JoystickButtons.DPAD_LEFT | JoystickButtons.BUTTON_Y],False,
                                                 JoystickButtons.BUTTON_Y],False,
                                        lambda : sys.stdout.write("<-----> LEFT ABUKE \n")))

if __name__ == '__main__':
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  # Initializing joystick support
  pygame.init()
  pygame.joystick.init()
  t = TestJoystickController()    
  t.run()
  pygame.joystick.quit()          
        

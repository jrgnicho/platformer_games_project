#!/usr/bin/env python
import sys
import logging
import rospkg
import pygame
from panda3d.core import Vec3
from physics_platformer.test import TestGame
from physics_platformer.resource_management.ff3 import CharacterLoader
from physics_platformer.character.character_states import CharacterStateKeys
from physics_platformer.game_actions import *
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.character.character_base import CharacterBase
from physics_platformer.character.character_states import CharacterStates
from physics_platformer.input import Move
from physics_platformer.input import KeyboardButtons
from physics_platformer.input import KeyboardController
from physics_platformer.input import JoystickButtons
from physics_platformer.input import JoystickController

RESOURCES_DIRECTORY = rospkg.RosPack().get_path('platformer_resources')+ '/characters/Hiei/'
PLAYER_DEF_FILE = RESOURCES_DIRECTORY + 'player.def'
ANIMATIONS = ['RUNNING','STANDING','TAKEOFF','ASCEND','FALL','LAND','AVOID_FALL','STAND_ON_EDGE','LAND_EDGE']

class Hiei(CharacterBase):
  
  def __init__(self,character_loader):
    self.character_loader_ = character_loader
    CharacterBase.__init__(self,character_loader.getCharacterInfo())
    
  def setup(self):
    if(not self.loadResources()):
      return False
    
    if (not self.setupStates()):
      return False
    
    return True
  
  def loadResources(self):
    animation_actors = self.character_loader_.getAnimationActors()
      
    anim_counter = 0
    for actor in animation_actors:
      
      if ANIMATIONS.count(actor.getName()) > 0:   
        anim_counter+=1          
        logging.debug("Animation Actor %s was found"%(actor.getName()))       
        self.addAnimationActor(actor.getName(),actor)
      else:
        logging.warn("Animation Actor %s was found but will not be loaded"%(actor.getName()))
        
    return anim_counter == len(ANIMATIONS)
  
  def setupStates(self):
    
    # creating default states
    standing_state = CharacterStates.StandingState(self, self.sm_,ANIMATIONS[1])
    running_state = CharacterStates.RunningState(self,self.sm_,ANIMATIONS[0])
    takeoff_state = CharacterStates.TakeoffState(self,self.sm_,ANIMATIONS[2])
    jump_state = CharacterStates.JumpState(self,self.sm_,ANIMATIONS[3])
    air_jump_state = CharacterStates.AirJumpState(self,self.sm_,ANIMATIONS[3])
    fall_state = CharacterStates.FallState(self,self.sm_,ANIMATIONS[4])
    land_state = CharacterStates.LandState(self,self.sm_,ANIMATIONS[5])
    standing_edge_recovery_state = CharacterStates.StandingEdgeRecovery(self,self.sm_,ANIMATIONS[6])
    standing_near_edge_state = CharacterStates.StandingNearEdge(self,self.sm_,ANIMATIONS[7])
    edge_landing_state = CharacterStates.EdgeLandingState(self,self.sm_,ANIMATIONS[8])
        
    self.sm_.addState(fall_state)
    self.sm_.addState(standing_state)
    self.sm_.addState(running_state)
    self.sm_.addState(takeoff_state)
    self.sm_.addState(jump_state)
    self.sm_.addState(air_jump_state)
    self.sm_.addState(land_state)  
    self.sm_.addState(standing_edge_recovery_state)
    self.sm_.addState(standing_near_edge_state) 
    self.sm_.addState(edge_landing_state) 
       
    
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.LAND.key, CharacterStateKeys.LANDING)
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.LAND_EDGE.key, CharacterStateKeys.EDGE_LANDING)
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.AIR_JUMP.key, CharacterStateKeys.AIR_JUMPING)
    
    self.sm_.addTransition(CharacterStateKeys.EDGE_LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CollisionAction.FREE_FALL,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.EDGE_RECOVERY.key,CharacterStateKeys.STANDING_EDGE_RECOVERY)    
    
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,StateMachineActions.DONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.MOVE_NONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CollisionAction.FREE_FALL,CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, StateMachineActions.DONE.key, CharacterStateKeys.JUMPING)
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.JUMPING, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.LANDING, CollisionAction.FREE_FALL, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.LANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    
    self.sm_.addTransition(CharacterStateKeys.AIR_JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    
    return True
    

class TestBasicGame(TestGame):
  
  def __init__(self,name):
    TestGame.__init__(self,name)
    
  def update(self,task):
    pygame.event.get()
    return TestGame.update(self,task)
    
  def setupScene(self):
    TestGame.setupScene(self)
    self.setupCharacter()
    
  def setupControls(self):
    
    TestGame.setupControls(self)
    
       # Input (Events)
    self.accept('f6', self.toggleCameraController)
    self.instructions_.append(self.createInstruction(0.54, "F6: Toggle Camera Controls"))
    
  def setupCharacter(self):
    
    logging.info("Loading Character resources")
    self.character_loader_ = CharacterLoader()
    if not self.character_loader_.load(PLAYER_DEF_FILE):
      logging.error("Failed to load player definition file %s"%(PLAYER_DEF_FILE))
      sys.exit()
      
    # loading animations into character
    info = self.character_loader_.getCharacterInfo()
    logging.info(str(info))
    self.character_ = Hiei(self.character_loader_)
    
    if not self.character_.setup():
      logging.error("Character setup failed")
      sys.exit()
      
    self.level_.addGameObject(self.character_)      
    self.character_.setPos(Vec3(5,0,self.character_.getSize().getZ()+8))     
    self.character_.pose(ANIMATIONS[4])    
    
    # create character keyboard controller
    self.character_input_manager_ = self.setupJoystickController()
    if self.character_input_manager_ is None:
      self.character_input_manager_ = self.setupKeyboardController()
    
    # setting camera relative to player
    self.camera_input_manager_ = self.input_manager_
    self.follow_player_ = True
    self.toggleCameraController()
    
  def setupKeyboardController(self):
    # create character keyboard controller
    button_map = {'a' : KeyboardButtons.KEY_A , 's' : KeyboardButtons.KEY_S,'d' : KeyboardButtons.KEY_D}
    keyboard_manager = KeyboardController(self.input_state_, button_map)
    
    # Creating press moves
    keyboard_manager.addMove(Move('UP',[KeyboardButtons.DPAD_UP],True, lambda : self.character_.execute(CharacterActions.MOVE_UP)))
    keyboard_manager.addMove(Move('DOWN',[KeyboardButtons.DPAD_DOWN],True,  lambda : self.character_.execute(CharacterActions.MOVE_DOWN)))
    keyboard_manager.addMove(Move('LEFT',[KeyboardButtons.DPAD_LEFT],True, lambda : self.character_.execute(CharacterActions.MOVE_LEFT)))
    keyboard_manager.addMove(Move('RIGHT',[KeyboardButtons.DPAD_RIGHT],True, lambda : self.character_.execute(CharacterActions.MOVE_RIGHT)))    
    keyboard_manager.addMove(Move('JUMP',[KeyboardButtons.KEY_S],True, lambda : self.character_.execute(CharacterActions.JUMP)))
    #keyboard_manager.addMove(Move('DASH',[KeyboardButtons.KEY_Q],False, lambda : self.character_.execute(CharacterActions.MOVE_UP)))
    
    # Creating release moves
    keyboard_manager.addMove(Move('HALT',[KeyboardButtons.DPAD_RIGHT],True, lambda : self.character_.execute(CharacterActions.MOVE_NONE)),False)
    keyboard_manager.addMove(Move('HALT',[KeyboardButtons.DPAD_LEFT],True, lambda : self.character_.execute(CharacterActions.MOVE_NONE)),False)    
    keyboard_manager.addMove(Move('JUMP_CANCEL',[KeyboardButtons.KEY_S],True, lambda : self.character_.execute(CharacterActions.JUMP_CANCEL)),False)
    
    return keyboard_manager
  
  def setupJoystickController(self):
    
    pygame.init()
    pygame.joystick.init()
    
    # Creating button map
    button_map = {0 : JoystickButtons.BUTTON_X , 3 : JoystickButtons.BUTTON_Y,
                  1 : JoystickButtons.BUTTON_A , 2 : JoystickButtons.BUTTON_B,
                  7 : JoystickButtons.TRIGGER_R1 , 5 : JoystickButtons.TRIGGER_R2,
                  6 : JoystickButtons.TRIGGER_L1 , 4 : JoystickButtons.TRIGGER_L2,
                  9 : JoystickButtons.BUTTON_START , 8 : JoystickButtons.BUTTON_SELECT,
                  10: JoystickButtons.TRIGGER_L3   , 11: JoystickButtons.TRIGGER_R3}
    

    if pygame.joystick.get_count() <=  0:
      logging.error("No Joysticks were found, exiting")
      return None
      
    joystick = None
    for j in range(0,pygame.joystick.get_count()):
      joystick = pygame.joystick.Joystick(j)
      if joystick.init() and joystick.get_numbuttons() > 0:
        break;
    
    joystick_manager = JoystickController(button_map,joystick, JoystickController.JoystickAxes(),2)
    
    joystick_manager.addMove(Move('LEFT',[JoystickButtons.DPAD_LEFT],True, lambda : self.character_.motion_commander_.moveLeft()))
    joystick_manager.addMove(Move('RIGHT',[JoystickButtons.DPAD_RIGHT],True, lambda : self.character_.motion_commander_.moveRight()))
    
    joystick_manager.addMove(Move('UP',[JoystickButtons.DPAD_UP],True, lambda : self.character_.execute(CharacterActions.MOVE_UP)))
    joystick_manager.addMove(Move('DOWN',[JoystickButtons.DPAD_DOWN],True,  lambda : self.character_.execute(CharacterActions.MOVE_DOWN)))
    joystick_manager.addMove(Move('JUMP',[JoystickButtons.BUTTON_B],True, lambda : self.character_.execute(CharacterActions.JUMP)))
    #joystick_manager.addMove(Move('DASH',[JoystickButtons.TRIGGER_R1],False, lambda : self.character_.execute(CharacterActions.MOVE_UP)))
    
    # Creating release moves
#     joystick_manager.addMove(Move('HALT',[JoystickButtons.DPAD_RIGHT],True, lambda : self.character_.execute(CharacterActions.MOVE_NONE)),False)
#     joystick_manager.addMove(Move('HALT',[JoystickButtons.DPAD_LEFT],True, lambda : self.character_.execute(CharacterActions.MOVE_NONE)),False)
    joystick_manager.addMove(Move('HALT',[JoystickButtons.DPAD_RIGHT],True, lambda : self.character_.motion_commander_.stop()),False)
    joystick_manager.addMove(Move('HALT',[JoystickButtons.DPAD_LEFT],True, lambda : self.character_.motion_commander_.stop()),False)
    joystick_manager.addMove(Move('JUMP_CANCEL',[JoystickButtons.BUTTON_B],True, lambda : self.character_.execute(CharacterActions.JUMP_CANCEL)),False)
    

    return joystick_manager
    
  def toggleCameraController(self):
    
    if self.follow_player_:
      self.input_manager_ = self.character_input_manager_      
      self.cam.reparentTo(self.character_)
      self.cam.setPos(self.character_,0, -TestGame.__CAM_ZOOM__*24, 0)
    else:
      self.input_manager_ = self.camera_input_manager_
      pos = self.cam.getPos(self.level_)
      self.cam.reparentTo(self.level_)
      self.cam.setPos(pos)
      
    self.follow_player_ = not self.follow_player_
    
  

if __name__ == "__main__":
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  g = TestBasicGame("BasicGame")
  g.run()
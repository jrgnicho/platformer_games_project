#!/usr/bin/env python3
import sys
import logging
import pygame
import os

from pathlib import Path

import  context

from panda3d.core import Vec3
from panda3d.bullet import BulletDebugNode

from platformer_core.test import TestGameBase
from platformer_core.resource_management.ff3 import CharacterLoader
from platformer_core.character.character_states import CharacterStateKeys
from platformer_core.game_actions import *
from platformer_core.state_machine import StateMachineActions
from platformer_core.character.character_base import CharacterBase
from platformer_core.character.character_states import CharacterStates
from platformer_core.input import Move
from platformer_core.input import KeyboardButtons
from platformer_core.input import KeyboardController
from platformer_core.input import JoystickButtons
from platformer_core.input import JoystickController
from platformer_core.camera import CameraController
from platformer_core.resource_management.level_loader import LevelLoader
from platformer_core.resource_management.assets_common import AssetsLocator

LEVEL_RESOURCE_PATH  = str(Path(AssetsLocator.get_platformer_assets_path()) / 'worlds/PlatformerSimpleLevel.egg')
RESOURCES_DIRECTORY = str(Path(AssetsLocator.get_platformer_assets_path()) / 'characters/Hiei/')
PLAYER_DEF_FILE = os.path.join(RESOURCES_DIRECTORY, 'player.def')
ANIMATIONS = ['STANDING','RUNNING','TAKEOFF','ASCEND','FALL','LAND','AVOID_FALL','STAND_ON_EDGE','LAND_EDGE', 'DASH', 'MIDAIR_DASH','CATCH_LEDGE','CLIMB_LEDGE']

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
    standing_state = CharacterStates.StandingState(self, self.sm_,ANIMATIONS[0])
    running_state = CharacterStates.RunningState(self,self.sm_,ANIMATIONS[1])
    takeoff_state = CharacterStates.TakeoffState(self,self.sm_,ANIMATIONS[2])
    jump_state = CharacterStates.JumpState(self,self.sm_,ANIMATIONS[3])
    air_jump_state = CharacterStates.AirJumpState(self,self.sm_,ANIMATIONS[3])
    fall_state = CharacterStates.FallState(self,self.sm_,ANIMATIONS[4])
    land_state = CharacterStates.LandState(self,self.sm_,ANIMATIONS[5])
    standing_edge_recovery_state = CharacterStates.StandingEdgeRecovery(self,self.sm_,ANIMATIONS[6])
    standing_near_edge_state = CharacterStates.StandingNearEdge(self,self.sm_,ANIMATIONS[7])
    edge_landing_state = CharacterStates.EdgeLandingState(self,self.sm_,ANIMATIONS[8])    
    dashing_state = CharacterStates.DashState(self,self.sm_,ANIMATIONS[9])
    midair_dashing_state = CharacterStates.MidairDashState(self,self.sm_,ANIMATIONS[10])
    catch_ledge_state = CharacterStates.CatchLedgeState(self,self.sm_,ANIMATIONS[11])
    climbing_state = CharacterStates.ClimbingState(self,self.sm_,ANIMATIONS[12])
        
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
    self.sm_.addState(dashing_state) 
    self.sm_.addState(midair_dashing_state)
    self.sm_.addState(catch_ledge_state)
    self.sm_.addState(climbing_state)
       
    
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.LAND.key, CharacterStateKeys.LANDING)
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.LAND_EDGE.key, CharacterStateKeys.EDGE_LANDING)
    self.sm_.addTransition(CharacterStateKeys.FALLING, CharacterActions.JUMP.key, CharacterStateKeys.AIR_JUMPING, lambda: self.getStatus().air_jumps_count < self.getInfo().air_jumps)
    self.sm_.addTransition(CharacterStateKeys.FALLING,CharacterActions.DASH.key,CharacterStateKeys.MIDAIR_DASHING,lambda: self.getStatus().air_dashes_count < self.getInfo().air_dashes)
    self.sm_.addTransition(CharacterStateKeys.FALLING, CollisionAction.LEDGE_ACTION_COLLISION, CharacterStateKeys.CATCH_LEDGE)
    
    self.sm_.addTransition(CharacterStateKeys.CATCH_LEDGE, CharacterActions.JUMP.key, CharacterStateKeys.JUMPING)
    self.sm_.addTransition(CharacterStateKeys.CATCH_LEDGE, CharacterActions.MOVE_UP.key, CharacterStateKeys.CLIMBING)
    
    self.sm_.addTransition(CharacterStateKeys.CLIMBING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    
    self.sm_.addTransition(CharacterStateKeys.EDGE_LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.EDGE_LANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.EDGE_LANDING,CharacterActions.DASH.key,CharacterStateKeys.DASHING)
    
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CollisionAction.FREE_FALL,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.FALL.key,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.EDGE_RECOVERY.key,CharacterStateKeys.STANDING_EDGE_RECOVERY) 
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.DASH.key,CharacterStateKeys.DASHING)   
    
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,StateMachineActions.DONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_EDGE_RECOVERY,CharacterActions.DASH.key,CharacterStateKeys.DASHING)
    
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING_NEAR_EDGE,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.MOVE_NONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CollisionAction.FREE_FALL,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.DASH.key,CharacterStateKeys.DASHING)
    
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, StateMachineActions.DONE.key, CharacterStateKeys.JUMPING)
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.JUMPING, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.JUMPING,CharacterActions.DASH.key,CharacterStateKeys.MIDAIR_DASHING,lambda: self.getStatus().air_dashes_count < self.getInfo().air_dashes)
    
    self.sm_.addTransition(CharacterStateKeys.LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.LANDING, CollisionAction.FREE_FALL, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.LANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.LANDING,CharacterActions.DASH.key,CharacterStateKeys.DASHING) 
    
    self.sm_.addTransition(CharacterStateKeys.AIR_JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.AIR_JUMPING, CharacterActions.JUMP_CANCEL.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.AIR_JUMPING, CharacterActions.DASH.key,CharacterStateKeys.MIDAIR_DASHING,lambda: self.getStatus().air_dashes_count < self.getInfo().air_dashes)
    
    self.sm_.addTransition(CharacterStateKeys.DASHING,StateMachineActions.DONE.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.DASHING,CharacterActions.DASH_CANCEL.key,CharacterStateKeys.STANDING)
    self.sm_.addTransition(CharacterStateKeys.DASHING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.DASHING,CharacterActions.FALL.key,CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,StateMachineActions.DONE.key,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,CharacterActions.JUMP.key,CharacterStateKeys.AIR_JUMPING,lambda: self.getStatus().air_jumps_count < self.getInfo().air_jumps)
    self.sm_.addTransition(CharacterStateKeys.MIDAIR_DASHING,CharacterActions.DASH_CANCEL.key,CharacterStateKeys.FALLING)
    
    return True
    

class TestBasicGame(TestGameBase):
  
  def __init__(self,name):
    self.sim_substeps_ = 20
    self.sim_step_size_ = 1/160.0
    TestGameBase.__init__(self,name)
    
  def update(self,task):
    pygame.event.get()
    return TestGameBase.update(self,task)
    
  def setupScene(self):
    #TestGameBase.setupScene(self)
    
    # Loading level
    level_loader = LevelLoader()
    self.level_ = level_loader.load(LEVEL_RESOURCE_PATH)
    if self.level_ is None:
      sys.exit(-1)
      
    #self.level_.physics_substeps = self.sim_substeps_
    #self.level_.physics_step_size = self.sim_step_size_
    
    self.level_.reparentTo(self.render)
    
    if level_loader.start_location is not None:
      logging.info('Start location is %s'%(str(level_loader.start_location.getPos(self.level_))))
    
    if level_loader.start_sector is not None:
      logging.info('Level %s start sector is "%s"'%(self.level_.getName(),level_loader.start_sector.getName()) )
    
    # enable debug visuals
    self.debug_node_ = self.level_.attachNewNode(BulletDebugNode('Debug'))
    self.debug_node_.node().showWireframe(True)
    self.debug_node_.node().showConstraints(True)
    self.debug_node_.node().showBoundingBoxes(False)
    self.debug_node_.node().showNormals(True)    
    self.level_.getPhysicsWorld().setDebugNode(self.debug_node_.node())    
    self.debug_node_.hide()
     
    self.camera_controller_ = CameraController(self.cam)
    self.camera_controller_.reparentTo(self.level_)
    self.camera_controller_.setEnabled(True)             

    # Character setup
    self.setupCharacter(level_loader.start_location, level_loader.start_sector)  
    
  def setupControls(self):
    
    TestGameBase.setupControls(self)
    
       # Input (Events)
    self.accept('f6', self.toggleCameraController)
    self.instructions_.append(self.createInstruction(0.54, "F6: Toggle Camera Controls"))
    
  def setupCharacter(self,start_location_np, start_sector):
    
    logging.info("Loading Character resources")
    self.character_loader_ = CharacterLoader()
    if not self.character_loader_.load(PLAYER_DEF_FILE):
      logging.error("Failed to load player definition file %s"%(PLAYER_DEF_FILE))
      sys.exit()
      
    # loading animations into character
    info = self.character_loader_.getCharacterInfo()
    logging.info(str(info))
    self.character_ = Hiei(self.character_loader_)
    
    # make player's sprites reorient to face camera  
    self.character_.setViewingNode(self.cam)
    
    if not self.character_.setup():
      logging.error("Character setup failed")
      sys.exit()
    
    # placing character in world    
    sector  = start_sector
    self.level_.addGameObject(self.character_)          
    self.character_.setPos(sector,start_location_np.getPos(sector))  
    sector.attach(self.character_)   
    sector.enableTransitions(True)
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
    button_map = {'a' : KeyboardButtons.KEY_A , 's' : KeyboardButtons.KEY_S,'d' : KeyboardButtons.KEY_D, 'q' : KeyboardButtons.KEY_Q}
    keyboard_manager = KeyboardController(self.input_state_, button_map, True)
    
    # Creating press moves
    keyboard_manager.addMove(Move('UP',[KeyboardButtons.DPAD_UP],True, lambda : self.character_.execute(CharacterActions.MOVE_UP)))
    keyboard_manager.addMove(Move('DOWN',[KeyboardButtons.DPAD_DOWN],True,  lambda : self.character_.execute(CharacterActions.MOVE_DOWN)))
    keyboard_manager.addMove(Move('LEFT',[KeyboardButtons.DPAD_LEFT],True, lambda : self.character_.motion_commander_.moveLeft() ))
    keyboard_manager.addMove(Move('RIGHT',[KeyboardButtons.DPAD_RIGHT],True, lambda : self.character_.motion_commander_.moveRight() ))    
    keyboard_manager.addMove(Move('JUMP',[KeyboardButtons.KEY_S],True, lambda : self.character_.execute(CharacterActions.JUMP)))
    keyboard_manager.addMove(Move('DASH',[KeyboardButtons.KEY_Q],False, lambda : self.character_.execute(CharacterActions.DASH)))
    
    # Creating release moves
    keyboard_manager.addMove(Move('HALT',[KeyboardButtons.DPAD_RIGHT],True, lambda : self.character_.motion_commander_.stop()),False)
    keyboard_manager.addMove(Move('HALT',[KeyboardButtons.DPAD_LEFT],True, lambda : self.character_.motion_commander_.stop()),False)    
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
    joystick_manager.addMove(Move('DASH',[JoystickButtons.TRIGGER_R1],True, lambda : self.character_.execute(CharacterActions.DASH)))
    
    # Creating release moves
    joystick_manager.addMove(Move('HALT',[JoystickButtons.DPAD_RIGHT],True, lambda : self.character_.motion_commander_.stop()),False)
    joystick_manager.addMove(Move('HALT',[JoystickButtons.DPAD_LEFT],True, lambda : self.character_.motion_commander_.stop()),False)
    joystick_manager.addMove(Move('JUMP_CANCEL',[JoystickButtons.BUTTON_B],True, lambda : self.character_.execute(CharacterActions.JUMP_CANCEL)),False)
    joystick_manager.addMove(Move('DASH_CANCEL',[JoystickButtons.TRIGGER_R1],True, lambda : self.character_.execute(CharacterActions.DASH_CANCEL)),False)
    

    return joystick_manager
    
  def toggleCameraController(self):
    
    if self.follow_player_:
      self.input_manager_ = self.character_input_manager_
      self.camera_controller_.reparentTo(self.level_)
      self.camera_controller_.setEnabled(True)      
      self.camera_controller_.setTargetNode(self.character_)
    else:
      ref_np = self.character_.getReferenceNodePath()
      self.input_manager_ = self.camera_input_manager_         
      tr = self.cam.getTransform(ref_np)
      self.camera_controller_.setEnabled(False)
      self.cam.reparentTo(ref_np)
      self.cam.setTransform(ref_np,tr)
      
    self.follow_player_ = not self.follow_player_
    
  

if __name__ == "__main__":
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  g = TestBasicGame("BasicGame")
  g.run()
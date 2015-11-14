#!/usr/bin/env python
import sys
import logging
import rospkg
from panda3d.core import Vec3
from physics_platformer.test import TestGame
from physics_platformer.resource_management.ff3 import CharacterLoader
from physics_platformer.character.character_states import CharacterStateKeys
from physics_platformer.game_actions import *
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.character.character_states import CharacterStates
from physics_platformer.character import Character

RESOURCES_DIRECTORY = rospkg.RosPack().get_path('platformer_resources')+ '/characters/Hiei/'
PLAYER_DEF_FILE = RESOURCES_DIRECTORY + 'player.def'
ANIMATIONS = ['RUNNING','STANDING','TAKEOFF','ASCEND','FALL','LAND']

class Hiei(Character):
  
  def __init__(self,character_loader):
    self.character_loader_ = character_loader
    Character.__init__(self,character_loader.getCharacterInfo())
    
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
        
    return anim_counter > 0
  
  def setupStates(self):
    # creating default states
    standing_state = CharacterStates.StandingState(self, self.sm_,ANIMATIONS[1])
    running_state = CharacterStates.RunningState(self,self.sm_,ANIMATIONS[0])
    takeoff_state = CharacterStates.TakeoffState(self,self.sm_,ANIMATIONS[2])
    jump_state = CharacterStates.JumpState(self,self.sm_,ANIMATIONS[3])
    fall_state = CharacterStates.FallState(self,self.sm_,ANIMATIONS[4])
    land_state = CharacterStates.LandState(self,self.sm_,ANIMATIONS[5])
        
    self.sm_.addState(fall_state)
    self.sm_.addState(standing_state)
    self.sm_.addState(running_state)
    self.sm_.addState(takeoff_state)
    self.sm_.addState(jump_state)
    self.sm_.addState(land_state)    
       
    
    self.sm_.addTransition(CharacterStateKeys.FALLING, CollisionAction.SURFACE_COLLISION, CharacterStateKeys.LANDING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_RIGHT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.MOVE_LEFT.key,CharacterStateKeys.RUNNING)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.STANDING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CollisionAction.COLLISION_FREE,CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.JUMP.key,CharacterStateKeys.TAKEOFF)
    self.sm_.addTransition(CharacterStateKeys.RUNNING,CharacterActions.MOVE_NONE.key,CharacterStateKeys.STANDING)
    
    self.sm_.addTransition(CharacterStateKeys.TAKEOFF, StateMachineActions.DONE.key, CharacterStateKeys.JUMPING)
    self.sm_.addTransition(CharacterStateKeys.JUMPING, StateMachineActions.DONE.key, CharacterStateKeys.FALLING)
    self.sm_.addTransition(CharacterStateKeys.LANDING, StateMachineActions.DONE.key, CharacterStateKeys.STANDING)
    
    return True
    

class TestBasicGame(TestGame):
  
  def __init__(self,name):
    TestGame.__init__(self,name)
    
  def setupScene(self):
    TestGame.setupScene(self)
    self.setupCharacter()
    
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
        
  

if __name__ == "__main__":
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  g = TestBasicGame("BasicGame")
  g.run()
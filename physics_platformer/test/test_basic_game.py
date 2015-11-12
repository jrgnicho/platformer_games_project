#!/usr/bin/env python
import sys
import logging
import rospkg
from panda3d.core import Vec3
from physics_platformer.test import TestGame
from physics_platformer.resource_management.ff3 import CharacterLoader
from physics_platformer.character import Character

RESOURCES_DIRECTORY = rospkg.RosPack().get_path('platformer_resources')+ '/characters/Hiei/'
PLAYER_DEF_FILE = RESOURCES_DIRECTORY + 'player.def'
ANIMATIONS = ['RUNNING','STANDING','TAKEOFF','ASCEND','FALL','LAND']

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
    self.character_ = Character(info)
    animation_actors = self.character_loader_.getAnimationActors()
      
    anim_counter = 0
    for actor in animation_actors:
      
      if ANIMATIONS.count(actor.getName()) > 0:             
        logging.debug("Animation Actor %s was found"%(actor.getName()))       
        self.character_.addAnimationActor(actor.getName(),actor)
    
    self.character_.setup()
    self.level_.addGameObject(self.character_)      
    self.character_.setPos(Vec3(5,0,self.character_.getSize().getZ()+10))     
    self.character_.pose(ANIMATIONS[4])    
        
  

if __name__ == "__main__":
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  g = TestBasicGame("BasicGame")
  g.run()
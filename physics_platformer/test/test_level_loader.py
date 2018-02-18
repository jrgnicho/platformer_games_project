#!/usr/bin/env python3

import sys
import logging
import rospkg
import pygame
import os
from panda3d.core import Vec3
from physics_platformer.test import TestGameBase
from physics_platformer.game_actions import *
from physics_platformer.state_machine import StateMachineActions
from physics_platformer.input import Move
from physics_platformer.input import KeyboardButtons
from physics_platformer.input import KeyboardController
from physics_platformer.resource_management import LevelLoader
from physics_platformer.camera import CameraController

from panda3d.bullet import BulletDebugNode


LEVEL_RESOURCE_PATH  = os.path.join(rospkg.RosPack().get_path('platformer_resources'),'worlds/PlatformerSimpleLevel.egg')

class TestLevelLoader(TestGameBase):
  
  def __init__(self,name):
    TestGameBase.__init__(self,name)
    
  def update(self,task):
    return TestGameBase.update(self,task)
    
  def setupScene(self):
    
    level_loader = LevelLoader()
    self.level_ = level_loader.load(LEVEL_RESOURCE_PATH)
    if self.level_ is None:
      sys.exit(-1)
    
    self.level_.reparentTo(self.render)
    
    # enable debug visuals
    self.debug_node_ = self.level_.attachNewNode(BulletDebugNode('Debug'))
    self.debug_node_.node().showWireframe(True)
    self.debug_node_.node().showConstraints(True)
    self.debug_node_.node().showBoundingBoxes(False)
    self.debug_node_.node().showNormals(True)    
    self.level_.getPhysicsWorld().setDebugNode(self.debug_node_.node())    
    self.debug_node_.hide()
    
    self.cam.reparentTo(self.level_)
    
    self.camera_controller_ = CameraController(self.cam)
    self.camera_controller_.reparentTo(self.level_)
    self.camera_controller_.setEnabled(True)            
    self.cam.setPos(self.level_,0, -TestGameBase.__CAM_ZOOM__*40, TestGameBase.__CAM_STEP__*25)  
    
  def setupBackgroundImage(self): 
    pass
    
  def setupControls(self):
    
    TestGameBase.setupControls(self)
      
  

if __name__ == "__main__":
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  g = TestLevelLoader("TestLevelLoader")
  g.run()


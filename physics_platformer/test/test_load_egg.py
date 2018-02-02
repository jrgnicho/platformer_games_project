#!/usr/bin/env python2
import sys
import logging
import rospkg
import getopt
import os
from physics_platformer.game_object import GameObject
from physics_platformer.test import TestApplication
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import loadPrcFileData
from panda3d.core import Vec3
from panda3d.core import ModelPool
from panda3d.core import Filename

# from direct.interval.LerpInterval import LerpFunc
# from direct.interval.FunctionInterval import Func
# from direct.interval.IntervalGlobal import Sequence
from direct.task.TaskManagerGlobal import taskMgr

# The lines below enable the Direct Session browser (Fails with python3)
loadPrcFileData("", "want-directtools #t")
loadPrcFileData("", "want-tk #t")

# Global Variables
NUM_BOXES = 20
BOX_SIDE_LENGTH = 0.4
RESOURCE_DIR = rospkg.RosPack().get_path('platformer_resources')
DEFAULT_EGG_PATH = os.path.join(RESOURCE_DIR,'worlds/PlatformerSimpleLevel.egg')

class TestLoadEgg(TestApplication):
    
    def __init__(self, egg_file_path):        
        
        self.egg_file_path = egg_file_path
        self.seq_ = None # Sequence used for checking end of animations
        TestApplication.__init__(self,"Test Load Egg")
        
    def __del__(self):
      self.cleanup()
                
    def setupControls(self):
      TestApplication.setupControls(self)
      
      self.accept('i',lambda: sys.stdout.write(str(taskMgr)))
      self.accept('p',lambda: self.printCamPos())
      self.instructions_.append(self.addInstructions(0.36, "i: Print TaskManager Info"))
      self.instructions_.append(self.addInstructions(0.44, 'p: Print Camera Position'))
      
    def printCamPos(self):
      pos = self.cam.getPos(self.world_node_)
      logging.info(str(pos))
        
    def setupResources(self):
      TestApplication.setupResources(self)

        
    def setupPhysics(self):
      
      TestApplication.setupPhysics(self,False)
      
      # loading egg model
      egg_model = NodePath(ModelPool.loadModel(Filename(self.egg_file_path)))
      egg_model.reparentTo(self.world_node_)     
      
      self.cam.setPos(self.world_node_,6.60001, -68, 14.4)
      
    def setupBoxes(self):
      
      box_size = Vec3(BOX_SIDE_LENGTH,BOX_SIDE_LENGTH,BOX_SIDE_LENGTH)
      start_pos = Vec3(-NUM_BOXES*BOX_SIDE_LENGTH*0.5,0,6)
      for i in range(0,NUM_BOXES):            
        obj = GameObject.createBox("obj"+str(i),box_size,True)
        obj.setPos(start_pos + Vec3(i*BOX_SIDE_LENGTH*0.5,0,i*BOX_SIDE_LENGTH*1.2))            
        obj.setPhysicsWorld(self.physics_world_)
        obj.reparentTo(self.world_node_)
        self.object_nodes_.append(obj)
          
        
    def cleanup(self):      
      TestApplication.cleanup(self)        


if __name__ == '__main__':
    
  # Setting up logging
  log_level = logging.DEBUG    
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)    
  
  egg_file_path = DEFAULT_EGG_PATH
  if len(sys.argv) > 2:
    # using default egg file
    egg_file_path = sys.argv[1]
      
    
  application = TestLoadEgg(egg_file_path)
  application.run()
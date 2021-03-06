#!/usr/bin/env python
import sys
import logging
import rospkg
import getopt
import os
from platformer_core.game_object import GameObject
from platformer_core.test import TestApplication
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import loadPrcFileData
from panda3d.core import Vec3
from panda3d.core import ModelPool
from panda3d.core import Filename

from direct.task.TaskManagerGlobal import taskMgr

# The lines below enable the Direct Session browser (Fails with python3)
loadPrcFileData("", "want-directtools #t")
loadPrcFileData("", "want-tk #t")

# Global Variables
NUM_BOXES = 20
BOX_SIDE_LENGTH = 0.4
RESOURCE_DIR = rospkg.RosPack().get_path('platformer_resources')
DEFAULT_EGG_PATH = os.path.join(RESOURCE_DIR,'worlds/PlatformerSimpleLevel.egg')
PYTHON_TAG = 'object_type'

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
      
    def printModelTree(self,model):
      
      def toTabChars(indentation_level):
        t = '  '
        return t*indentation_level
      
      def printNode(np,depth):        
               
        # print node name
        print(toTabChars(depth) + '-' + np.getName())   
        
        # extracting tag
        tag = np.getTag(PYTHON_TAG)
        attrib = ''
        if tag is not None:          
          attrib = '(%s: %s)'%(PYTHON_TAG,tag) 
          print(toTabChars(depth) + '  ' + attrib) 
          
        # printing position
        pos = np.getPos()
        print(toTabChars(depth) + '  Pos:' + str(pos))  
          
        if np.getNumChildren() > 0:
          print(toTabChars(depth) + '  Children:')          
          depth +=2
          for c in np.getChildren():
            printNode(c,depth)
            
          
      depth = 1
      printNode(model,depth)
              
    def setupPhysics(self):
      
      TestApplication.setupPhysics(self,False)
      
      # loading egg model
      egg_model = NodePath(ModelPool.loadModel(Filename(self.egg_file_path)))
      egg_model.reparentTo(self.world_node_)       
      
      self.cam.setPos(self.world_node_,6.60001, -68, 14.4)
      
      # printing loaded egg model
      self.printModelTree(egg_model)
      
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

#!/usr/bin/env python3

from direct.interval.Interval import Interval
from physics_platformer.test import TestApplication
from physics_platformer.game_object import *
from physics_platformer.sprite import SpriteLoader
from physics_platformer.animation import *
from physics_platformer.resource_management.ff3 import CharacterLoader
from physics_platformer.character.character_base import CharacterBase
import rospkg
from direct.interval.LerpInterval import LerpFunc
from direct.interval.FunctionInterval import Func
from direct.interval.IntervalGlobal import Sequence
import sys
import logging
import getopt
from direct.task.TaskManagerGlobal import taskMgr


NUM_BOXES = 20
BOX_SIDE_LENGTH = 0.4
SPRITE_SCALE = 1.0/40.0 # units/pixel

class SpriteDetails(object):
    
    def __init__(self,name,path,cols,rows,framerate):
        
        self.name = name
        self.path = path
        self.cols = cols
        self.rows = rows
        self.framerate = framerate

RESOURCES_DIRECTORY = rospkg.RosPack().get_path('platformer_resources')+ '/characters/Hiei/'
PLAYER_DEF_FILE = RESOURCES_DIRECTORY + 'player.def'
ANIMATIONS = ['RUNNING', 'SLASH0','STANDING','TAKEOFF','ASCEND','FALL','LAND','CATCH_LEDGE',
              'HANG_LEDGE', 'CLIMB_LEDGE', 'DASH', 'AVOID_FALL', 'STAND_ON_LEDGE', 'AIR_DASH']

class TestCharacterBase(TestApplication):
    
    def __init__(self):        
        
        self.seq_ = None # Sequence used for checking end of animations
        self.loop_ = True
        self.character_ = None
        self.character_loader_ = None
        self.animation_names_ = []
        TestApplication.__init__(self,"Test Animatable Object")
                
    def setupControls(self):
        TestApplication.setupControls(self)
        
        self.accept('n',self.nextAnimation)
        self.accept('b',self.toggleLeftRight)
        self.accept('l',self.loop )
        self.accept('p',self.play )
        self.accept('i',lambda: sys.stdout.write(str(taskMgr)))
        self.instructions_.append(self.addInstructions(0.36, "n: Next Animation"))
        self.instructions_.append(self.addInstructions(0.42, "b: Toggle Left Right"))
        self.instructions_.append(self.addInstructions(0.48, "l: Loop Animation"))
        self.instructions_.append(self.addInstructions(0.54, "p: Play Animation"))
        self.instructions_.append(self.addInstructions(0.60, "i: Print TaskManager Info"))
        
    def play(self):
        n = self.controlled_obj_.getCurrentAnimation()
        self.controlled_obj_.play( n ) 
        
    def loop(self):
        n = self.controlled_obj_.getCurrentAnimation()
        self.controlled_obj_.loop( n ) 
        
    def setupResources(self):
      TestApplication.setupResources(self)
      
      logging.info("Loading Character")
      character_loader = CharacterLoader()
      if not character_loader.load(PLAYER_DEF_FILE):
        logging.error("Failed to load player definition file %s"%(PLAYER_DEF_FILE))
        sys.exit()
        
      self.character_loader_ = character_loader
            
    def setupCharacter(self):
      
      info = self.character_loader_.getCharacterInfo()
      logging.info(str(info))
      self.character_ = CharacterBase(info)
      animation_actors = self.character_loader_.getAnimationActors()
      
      anim_counter = 0
      for actor in animation_actors:
        
        if ANIMATIONS.count(actor.getName()) > 0:             
          logging.info("Animation Actor %s was found"%(actor.getName()))       
          self.character_.addAnimationActor(actor.getName(),actor)
          self.animation_names_.append(actor.getName())
        else:
          pass
          #logging.warn("Animation Actor %s not found in list"%(actor.getName()))
          
      if len(self.animation_names_) == 0 :
        logging.error("Failed to add animation actors into CharacterBase")
        sys.exit()
        
    def setupPhysics(self):
        
        TestApplication.setupPhysics(self)
        self.setupCharacter()
        
        box_size = Vec3(BOX_SIDE_LENGTH,BOX_SIDE_LENGTH,BOX_SIDE_LENGTH)
        start_pos = Vec3(-NUM_BOXES*BOX_SIDE_LENGTH*0.5,0,6)
        for i in range(0,NUM_BOXES):            
            obj = GameObject.createBox("obj"+str(i),box_size,True)
            obj.setPos(start_pos + Vec3(i*BOX_SIDE_LENGTH*0.5,0,i*BOX_SIDE_LENGTH*1.2))            
            obj.setPhysicsWorld(self.physics_world_)
            obj.reparentTo(self.world_node_)
            self.object_nodes_.append(obj)
            
        
        self.character_.setPhysicsWorld(self.physics_world_)     
        self.character_.reparentTo(self.world_node_)       
        self.character_.setPos(Vec3(1,0,self.character_.getSize().getZ()+1))  
        #self.character_.getRigidBody().reparentTo(self.world_node_)
        #self.physics_world_.attachRigidBody(self.character_.getRigidBody().node())
        self.controlled_obj_ =  self.character_
        self.animation_index_ = 0
        
        # setting up animation callbacks
        self.controlled_obj_.setAnimationEndCallback(lambda : logging.info("Animation %s completed"%(self.controlled_obj_.getCurrentAnimation())))
        self.controlled_obj_.setAnimationStartCallback(lambda : logging.info("Animation %s started"%(self.controlled_obj_.getCurrentAnimation())))
        
        self.nextAnimation()
        
        self.cam.setX(self.character_.getPos().getX())
        self.cam.setPos(self.character_,0, -16, 0)
        
    def cleanup(self):
      
        self.physics_world_.remove(self.controlled_obj_.node())
        self.controlled_obj_.removeNode()
        self.controlled_obj_ = None
        self.character_ = None
        TestApplication.cleanup(self)
        
    # _____HANDLERS_____       
    
    def nextAnimation(self):
        
        self.animation_index_+=1
        if self.animation_index_ >= len(self.animation_names_):
            # reset the animation index
            self.animation_index_ = 0            
                
        anim_name = self.animation_names_[self.animation_index_]
        logging.debug("Selecting Character Animation %s"%(anim_name))
        self.controlled_obj_.pose(anim_name)
        logging.debug("Selected Character Animation %s"%(anim_name))
        
        
    def toggleLooping(self):
        self.loop_ = not self.loop_
        
    def toggleLeftRight(self):        

        dir = (not self.controlled_obj_.isFacingRight())
        self.controlled_obj_.faceRight(dir)


if __name__ == '__main__':
    
    
    log_level = logging.DEBUG
    try:
        opts, args = getopt.getopt(sys.argv[1:],'l:','log=')
    except getopt.GetoptError:
        logging.error("Invalid use of the %s script"%(sys.argv[0]))
        sys.exit()
        
    for opt,arg in opts:
        if opt in ('-l','--log'):
            
            # Configuring logging level
            log_level = getattr(logging, arg.upper(), None)
            if isinstance(log_level, int):                                
                print("Configuring log level to %s"%(arg.upper()))
        
    
    logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)    
    application = TestCharacterBase()
    application.run()

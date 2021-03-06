#!/usr/bin/env python3

from direct.interval.Interval import Interval
from platformer_core.test import TestApplication
from platformer_core.game_object import *
from platformer_core.sprite import SpriteLoader
from platformer_core.animation import *
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

SPRITES_DIRECTORY = rospkg.RosPack().get_path('simple_platformer')+ '/resources/hiei_sprites/animation/'
SPRITE_IMAGE_DETAILS = {'RUN'  : SpriteDetails('RUN',SPRITES_DIRECTORY + 'hiei_run_0-7.png',8,1,12),
                        'WALK' : SpriteDetails('DASH',SPRITES_DIRECTORY +'hiei_dash_0-2.png',3,1,12),
                        'JUMP' : SpriteDetails('JUMP',SPRITES_DIRECTORY +'hiei_jump_ascend_0-4.png',5,1,12),
                        'LAND' : SpriteDetails('LAND',SPRITES_DIRECTORY +'hiei_jump_land_0-2.png',3,1,12)}

class TestAnimatableObject(TestApplication):
    
    def __init__(self):        
        
        self.seq_ = None # Sequence used for checking end of animations
        self.loop_ = True
        self.setupResources()        
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
        
        sprite_loader = SpriteLoader()        
        sprite_animator_set = []
        
        for v in list(SPRITE_IMAGE_DETAILS.values()):
            success, right_imgs = sprite_loader.loadSpriteImages(v.path,v.cols,v.rows,False,False)
            if not success:
                logging.error(' Failed to load sprite images')
                sys.exit(1)
                
            left_imgs = sprite_loader.flipImages(right_imgs,True,False)
            anim_actor = AnimationActor(v.name)
            anim_actor.loadImages(right_imgs, left_imgs, v.framerate)
            anim_actor.setScale(Vec3(SPRITE_SCALE,1,SPRITE_SCALE))
            sprite_animator_set.append(anim_actor)
        self.animator_set_ = sprite_animator_set    
        
    def setupPhysics(self):
        
        TestApplication.setupPhysics(self)
        
        box_size = Vec3(BOX_SIDE_LENGTH,BOX_SIDE_LENGTH,BOX_SIDE_LENGTH)
        start_pos = Vec3(-NUM_BOXES*BOX_SIDE_LENGTH*0.5,0,6)
        for i in range(0,NUM_BOXES):            
            obj = GameObject.createBox("obj"+str(i),box_size,True)
            obj.setPos(start_pos + Vec3(i*BOX_SIDE_LENGTH*0.5,0,i*BOX_SIDE_LENGTH*1.2))
            self.physics_world_.attachRigidBody(obj.node())
            obj.reparentTo(self.world_node_)
            self.object_nodes_.append(obj)
            
            
        # Setting up animatable object
        actor2d = AnimatableObject('actor2d', Vec3(0.6,0.2,1), 1)        
        for anim in self.animator_set_:
            actor2d.addSpriteAnimation(anim.getName(), anim, AnimationSpriteAlignment.BOTTOM_CENTER_ALIGN)
        
        actor2d.setPos(Vec3(1,0,actor2d.getSize().getZ()+1))  
        actor2d.reparentTo(self.world_node_)
        self.physics_world_.attachRigidBody(actor2d.node())
        self.controlled_obj_ =  actor2d
        self.animation_index_ = 0
        
        # setting up animation callbacks
        self.controlled_obj_.setAnimationEndCallback(lambda : logging.info("Animation %s completed"%(self.controlled_obj_.getCurrentAnimation())))
        self.controlled_obj_.setAnimationStartCallback(lambda : logging.info("Animation %s started"%(self.controlled_obj_.getCurrentAnimation())))
        
        self.nextAnimation()
        
        self.cam.setX(actor2d.getPos().getX())
        self.cam.setPos(actor2d,0, -16, 0)
        
    def cleanup(self):
                
        self.physics_world_.removeRigidBody(self.controlled_obj_.node())
        self.controlled_obj_.removeNode()
        self.controlled_obj_ = None
        TestApplication.cleanup(self) 
        
    # _____HANDLERS_____       
    
    def nextAnimation(self):
        
        self.animation_index_+=1
        if self.animation_index_ >= len(self.animator_set_):
            # reset the animation index
            self.animation_index_ = 0            
            
        self.controlled_obj_.pose(self.animator_set_[self.animation_index_].getName())
        
        
    def toggleLooping(self):
        self.loop_ = not self.loop_
        
    def toggleLeftRight(self):        

        dir = (not self.controlled_obj_.isFacingRight())
        self.controlled_obj_.faceRight(dir)


if __name__ == '__main__':
    
    
    log_level = logging.WARN
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
    application = TestAnimatableObject()
    application.run()

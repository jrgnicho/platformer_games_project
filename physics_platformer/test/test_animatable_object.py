#!/usr/bin/env python

from physics_platformer.test import TestApplication
from physics_platformer.game_object import *
import rospkg
from docutils.nodes import colspec


NUM_BOXES = 20
BOX_SIDE_LENGTH = 0.4

class SpriteDetails(object):
    
    def __init__(self,name,path,cols,rows,framerate):
        
        self.name = name
        self.path = path
        self.cols = cols
        self.rows = rows
        self.framerate = framerate

SPRITES_DIRECTORY = rospkg.RosPack().get_path('simple_platformer')+ '/resources/hiei_sprites/animation/'
SPRITE_IMAGE_DETAILS = {'RUN'  : SpriteDetails('RUN',SPRITES_DIRECTORY + 'hiei_run_0-7.png',8,1,12),
                        'WALK' : SpriteDetails('WALK','models/hiei_run_0-7.png',8,1,12),
                        'JUMP' : SpriteDetails('JUMP','models/hiei_run_0-7.png',8,1,12),
                        'LAND' : SpriteDetails('JUMP','models/hiei_run_0-7.png',8,1,12)}

class TestAnimatableObject(TestApplication):
    
    def __init__(self):
        TestApplication.__init__(self,"Test Animatable Object")
        
    def setupPhysics(self):
        
        TestApplication.setupPhysics(self)
        
        box_size = Vec3(BOX_SIDE_LENGTH,BOX_SIDE_LENGTH,BOX_SIDE_LENGTH)
        start_pos = Vec3(-NUM_BOXES*BOX_SIDE_LENGTH*0.5,0,6)
        for i in range(0,NUM_BOXES):            
            obj = GameObject("obj"+str(i),box_size,True)
            obj.setPos(start_pos + Vec3(i*BOX_SIDE_LENGTH*0.5,0,i*BOX_SIDE_LENGTH*1.2))
            
            self.physics_world_.attachRigidBody(obj.node())
            obj.reparentTo(self.world_node_)
            self.object_nodes_.append(obj)
        


if __name__ == '__main__':
    application = TestAnimatableObject()
    application.run()

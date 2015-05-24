#!/usr/env/bin python

#from physics_platformer.game_object import *
from physics_platformer.test import TestApplication
import rospkg

RESOURCES_DIR = rospkg.RosPack().get_path('simple_platformer')   

application = TestApplication()


if __name__ == '__main__':
    application.run()

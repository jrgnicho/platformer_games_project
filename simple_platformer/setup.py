#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup()
d['packages'] = ['simple_platformer']
d['package_dir'] = {'': 'src'}

setup(**d)

#import rospkg
#import sys
#rospack = rospkg.RosPack()
#d = rospack.get_path('simple_platformer') + '/src'
#print "simple_platformer package path: %s"%(d)
#sys.path.insert(1,d)

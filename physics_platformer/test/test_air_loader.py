#!/usr/bin/env python

"""
Test of AIR file reader

This utility will read sprites from an FFE file generated with Fighter Factory 3

"""

from StringIO import StringIO
from PIL import Image
from physics_platformer.resource_management.ff3 import *
from panda3d.core import PNMImage, StringStream
from panda3d.core import Texture
from panda3d.core import LColor
import logging
import sys
import os

def main():

  air_file =''
  output_dir=''

  if len(sys.argv) >= 2:
    air_file = sys.argv[1]
  
  else:
    logging.error('Usage: test_air_loader air_file_path')
    return 
  
  if len(sys.argv) >= 3:
    output_dir = sys.argv[2]
  

  #checking output dir
  if (output_dir != '') and (not os.path.exists(output_dir)):
      os.makedirs(output_dir)
  else:
    logging.info("Output directory not set from command line, skipping image save")

    air_loader  = AIRLoader()
    air_loader.load(air_file)

if __name__ == '__main__':
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level) 

  main()
#!/usr/bin/env python3

"""
FFE Read for python

This utility will read sprites from an FFE file generated with Fighter Factory 3

"""

from io import StringIO
from PIL import Image
from platformer_core.resource_management.ff3 import FFELoader
from panda3d.core import PNMImage, StringStream
from panda3d.core import Texture
from panda3d.core import LColor
import logging
import sys
import os

def main():

  ffe_file =''
  output_dir=''

  if len(sys.argv) >= 2:
    ffe_file = sys.argv[1]
  
  else:
    logging.error('Usage: test_ffe_loader filename')
    return 
  
  if len(sys.argv) >= 3:
    output_dir = sys.argv[2]
  

  #checking output dir
  if (output_dir != '') and (not os.path.exists(output_dir)):
      os.makedirs(output_dir)
  else:
    logging.info("Output directory not set from command line, skipping image save")

    ffe_loader  = FFELoader()
    ffe_loader.load(ffe_file,[0,20,50])

if __name__ == '__main__':
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level) 

  main()


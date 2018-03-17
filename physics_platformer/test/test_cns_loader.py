#!/usr/bin/env python3

"""
Test of CNS file reader

This utility will character information from a .cns file generated with Fighter Factory 3

"""

from physics_platformer.resource_management.ff3 import CNSLoader
from physics_platformer.game_object import CharacterInfo
import logging
import sys
import os

def main():

  cns_file =''
  output_dir=''

  if len(sys.argv) >= 2:
    cns_file = sys.argv[1]
  
  else:
    logging.error('Usage: test_cns_loader cns_file_path')
    return 
    

  cns_loader  = CNSLoader()
  if cns_loader.load(cns_file):
    logging.info(str(cns_loader.getCharacterInfo()))
  else:
    logging.error("Failed to parse cns file %s",cns_file)

if __name__ == '__main__':
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level) 

  main()
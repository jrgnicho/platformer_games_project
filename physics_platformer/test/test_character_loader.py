#!/usr/bin/env python3

from physics_platformer.resource_management.ff3 import CharacterLoader
import logging
import os
import sys

def main():
  
  def_file = ''
  
  if len(sys.argv) >= 2:
    def_file = sys.argv[1]
  else:
    logging.error("Usage: test_character_loader [.def file path] ")
    return
    
    
  character_loader = CharacterLoader()
  if not character_loader.load(def_file):
    return
  
  for anim in character_loader.getAnimations():
    print(str(anim))
    
    
if __name__ == '__main__':
  
  logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG) 
  
  main()
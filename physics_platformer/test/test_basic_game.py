#!/usr/bin/env python
import logging
from physics_platformer.test import TestGame

if __name__ == "__main__":
  
  log_level = logging.DEBUG
  logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
  
  g = TestGame("BasicGame")
  g.run()
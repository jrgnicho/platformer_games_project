import sys

# Global constants

# Colors
class Colors(object):
    BLACK    = (   0,   0,   0)
    WHITE    = ( 255, 255, 255)
    BLUE     = (   0,   0, 255)
    RED      = ( 255,   0,   0)
    GREEN    = (   0, 255,   0)
        
class ScreenProperties(object):
    
    # Screen dimensions
    SCREEN_WIDTH  = 1000
    SCREEN_HEIGHT = 650

class GameProperties(object):
    
    FRAME_RATE = 60
    GRAVITY_ACCELERATION = 0.35 # pixels per second square
    
class TerminalColorCodes(object):
    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
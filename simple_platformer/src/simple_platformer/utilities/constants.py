import sys

# Global constants

# Colors
class Colors:
    BLACK    = (   0,   0,   0)
    WHITE    = ( 255, 255, 255)
    BLUE     = (   0,   0, 255)
    RED      = ( 255,   0,   0)
    GREEN    = (   0, 255,   0)
        
class ScreenProperties:
    
    # Screen dimensions
    SCREEN_WIDTH  = 1000
    SCREEN_HEIGHT = 650

class GameProperties:
    
    FRAME_RATE = 40
    GRAVITY_ACCELERATION = 0.35 # pixels per second square
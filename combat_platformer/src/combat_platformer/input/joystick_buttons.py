from bitarray import bitarray

class JoystickButtons:
    
    # directions
    NONE            =   bitarray('0000000000000000')
    DPAD_UP         =   bitarray('0000000000000001')
    DPAD_DOWN       =   bitarray('0000000000000010') 
    DPAD_LEFT       =   bitarray('0000000000000100')
    DPAD_RIGHT      =   bitarray('0000000000001000')    
    DPAD_UPRIGHT    =   DPAD_UP | DPAD_RIGHT
    DPAD_UPLEFT     =   DPAD_UP | DPAD_LEFT
    DPAD_DOWNRIGHT  =   DPAD_DOWN | DPAD_RIGHT
    DPAD_DOWNLEFT   =   DPAD_DOWN | DPAD_LEFT
    BUTTON_A        =   bitarray('0000000000010000')
    BUTTON_B        =   bitarray('0000000000100000')
    BUTTON_X        =   bitarray('0000000001000000')
    BUTTON_Y        =   bitarray('0000000010000000')
    TRIGGER_R1      =   bitarray('0000000100000000')
    TRIGGER_R2      =   bitarray('0000001000000000')
    TRIGGER_L1      =   bitarray('0000010000000000')
    TRIGGER_L2      =   bitarray('0000100000000000')
    BUTTON_START    =   bitarray('0001000000000000')
    BUTTON_SELECT   =   bitarray('0010000000000000')
    
    
from bitarray import bitarray

class JoystickButtons:
    
    # directions
    DPAD_UP     =   bitarray('0000000000000001')
    DPAD_DOWN   =   bitarray('0000000000000010') 
    DPAD_LEFT   =   bitarray('0000000000000100')
    DPAD_RIGHT  =   bitarray('0000000000001000')    
    BUTTON_A    =   bitarray('0000000000010000')
    BUTTON_B    =   bitarray('0000000000100000')
    BUTTON_X    =   bitarray('0000000001000000')
    BUTTON_Y    =   bitarray('0000000010000000')
    
    
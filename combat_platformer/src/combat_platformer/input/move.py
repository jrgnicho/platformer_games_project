from input import JoystickButtons

class Move(object):
    """
        Move(name,button_sequence,is_submove,callback)
        Inputs:
            - name             : String containing the name for the move
            - button_sequence  : List containing JoystickButton or Keyboard bitmasks for activating the move
            - is_submove : True | False indicating if this move is part of a larger move
            - callback : The function that will be executed when the execute() method is invoked
    """
    
    def __init__(self,name,button_sequence,is_submove,callback = None):
        
        self.name = name
        self.button_sequence = button_sequence;
        self.callback = callback if (callback != None) else (lambda : "Move %s executed"%(name))
        self.is_submove = is_submove
        
    def match(self,sequence):
        """
            match(sequence)            
            Checks is 'sequence' matches the button sequence in this move.
            Inputs:
                - sequence : List of button bitmasks
            Outputs:
                - Bool : True if match is found, false otherwise
        """
        
        if len(sequence) == len(self.button_sequence):
            for i in range(len(sequence)):
                if sequence[i] != self.button_sequence[i]:
                    return False
                #endif
            #endfor
                            
        else:
            return False
        #endif
        
        return True  
    
    def __len__(self):
        return len(self.button_sequence)
        
    def execute(self):
        """
            execute()
            Executes this moves callback
        """
        self.callback()
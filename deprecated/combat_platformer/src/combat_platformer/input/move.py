import sys
from combat_platformer.input import JoystickButtons

class Move(object):
    """
        Move(name,button_sequence,is_submove,callback)
        Inputs:
            - name             : String containing the name for the move
            - button_sequence  : List containing a JoystickButton list that activates the move
            - is_submove : True | False indicating if this move is part of a larger move
            - callback : The function that will be executed when the execute() method is invoked
    """
    
    def __init__(self,name,button_sequence,is_submove = False,callback = None):
        
        self.name = name
        self.button_sequence = button_sequence;
        self.callback = callback if (callback != None) else (lambda : sys.stdout.write("Move '%s' executed\n"%(name)))
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
        
        if len(sequence) >= len(self.button_sequence):
            
            # finding the first button entry
            if sequence.count(self.button_sequence[0]) > 0 :
                start_ind = sequence.index(self.button_sequence[0])
                subsequence = sequence[start_ind:]
                                
                # Exit if subsequence has fewer entries
                if len(subsequence) < len(self.button_sequence):
                    return False
            
                
                for i in range(len(self.button_sequence)):
                    if (subsequence[i] & self.button_sequence[i]) != self.button_sequence[i]:
                        return False
                    #endif
                #endfor
            else:
                # Button 'sequence' array doesn't have the first button entry
                return False
                            
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
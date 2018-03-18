
class Action(object):
  
  def __init__(self,key):
    self.key = key
    

class StateMachineActions(object):
    
    IGNORE = Action('IGNORE')
    SUBMACHINE_START = Action('SUBMACHINE_START')
    SUBMACHINE_RESTART = Action('SUBMACHINE_RESTART')
    SUBMACHINE_PAUSE = Action('SUBMACHINE_PAUSE')
    SUBMACHINE_STOP = Action('SUBMACHINE_STOP')
    DONE = Action('DONE')
    
    
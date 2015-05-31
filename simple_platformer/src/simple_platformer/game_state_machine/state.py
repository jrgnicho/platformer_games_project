import sys
import logging
    
class State(object):
    
    def __init__(self,state_key,entry_cb = None,exit_cb = None):
        
        self.key = state_key
        self.actions = {} # dictionary of actions (keys) and their corresponding callbacks
        self.entry_callback= entry_cb
        self.exit_callback = exit_cb
        
    def set_entry_callback(self,entry_cb):
        
        self.entry_callback = entry_cb
        
    def set_exit_callback(self,exit_cb):
        
        self.exit_callback = exit_cb        
        
    def add_action(self,action_key,
                       action_cb = lambda: logging.debug("No action callback\n")):
        """
        Adds supported action to the state
        
        Inputs:
        - action_key: action key for the action that can be executed during this state
        - action_cb: method that is invoked when this action is requested through the execute() method.
        """
        self.actions[action_key] = action_cb
        
    def has_action(self,action_key):
        
        return self.actions.has_key(action_key)
        
    def execute(self,action_key,action_cb_args=()):
        """
            Invokes the callback corresponding to this action upon entering this state.  
            
            Inputs:
            - action_key: action to be executed.
            - action_cb_args: tuple containing optional arguments to the registered action_callback
            Outputs:
            - Succeeded: True when action is registered within state.  False otherwise
                    
        """
        
        if self.actions.has_key(action_key):
            
            action_cb = self.actions[action_key]
            action_cb(*action_cb_args)
            #condition_cb = action_tuple[1]
            return True
        else:
            #print "State %s does not support %s action"%(self.key,action_key)
            return False
        
    def enter(self):
        
        if self.entry_callback != None:
            self.entry_callback()
        
    def exit(self):
        
        if self.exit_callback != None:
            self.exit_callback()
            
    @property
    def action_keys(self):
        return self.actions.keys()
    
        
        
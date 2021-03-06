import sys
from platformer_core.state_machine import Action
    
class State(object):
    
  def __init__(self,state_key,entry_cb = None,exit_cb = None):
      
      self.key_ = state_key
      self.actions_dict_ = {} # dictionary of actions (keys) and their corresponding callbacks
      self.entry_callback_= entry_cb
      self.exit_callback_ = exit_cb
      
  
  def setEntryCallback(self,entry_cb):
      
      self.entry_callback_ = entry_cb
  
  def setExitCallback(self,exit_cb):
      
      self.exit_callback_ = exit_cb        
      
  def addAction(self,action_key,
                     action_cb = lambda action : sys.stdout.write("No action callback\n")):
                      # ,condition_cb = lambda: True):
      """
      Adds supported action to the state
      
      Inputs:
      - action_key: action key for the action that can be executed during this state
      - action_cb: method that is invoked when this action is requested through the execute() method.
      """
      self.actions_dict_[action_key] = action_cb
      
  def hasAction(self,action_key):
      
      return action_key in self.actions_dict_
      
  def execute(self,action,action_cb_args=()):
      """
        execute(Action action)
          Invokes the callback corresponding to this action upon entering this state.  
          
          Inputs:
          - action: action to be executed.
          - action_cb_args: tuple containing optional arguments to the registered action_callback
          Outputs:
          - Succeeded: True when action is registered within state.  False otherwise
                  
      """
      
      if action.key in self.actions_dict_:
          
          action_cb = self.actions_dict_[action.key]
          action_cb(action)
          #condition_cb = action_tuple[1]
          return True
      else:
          #print "State %s does not support %s action"%(self.key_,action_key)
          return False
      
  def getKey(self):
      return self.key_
      
  def enter(self):
      
      if self.entry_callback_ != None:
          self.entry_callback_()
      
  def exit(self):
      
      if self.exit_callback_ != None:
          self.exit_callback_()
          
  def getActionKeys(self):
      return list(self.actions_dict_.keys())
        
        
        

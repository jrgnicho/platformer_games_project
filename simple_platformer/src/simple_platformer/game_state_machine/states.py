import sys

class StateKeys:
    
    NONE=""
    STANDING="STANDING"
    WALKING="WALKING"
    JUMPING="JUMPING"
    FALLING="FALLING"
    LANDING="LANDING"
    
class State:
    
    def __init__(self,state_key):
        
        self.key = state_key
        self.transitions = {}
        
        
    def add_transition(self,action_key,
                       next_state_key, 
                       action_cb = lambda: sys.stdout.write("No action callback\n"),
                       condition_cb = lambda: True):
        """
        Adds transition rule to the state
        
        Inputs:
        - action_key: action key for which this transition rule applies
        - next_state_key: state to transition to after action callback is executed.
        - action_cb: function to execute during this action
        - condition_cb: callback that checks a condition and returns either True or False.  When True, the 
            transition will be validated and the next_state_key will be returned by the execute() method.  
            If False then execute() will return the current state and no transition will be made.
            For instance, the callback could potentially check an interval threshold from <0,1> at which the transition
            is permitted
        """
        self.transitions[action_key] = (next_state_key,action_cb,condition_cb)
        
    def has_transition_rule(self,action_key):
        
        return self.transitions.has_key(action_key)
        
    def execute(self,action_key,action_cb_args=()):
        """
            Executes the requested action on this state.  A transition is made to another state if
            the condition callback registered for this action evaluates to True.  Otherwise no transition 
            is made.  The returned argument is key value for the next state when the transition is permitted.
            The current state is returned if a transition rule has not been added for this action or the requested
            transition was not validated.
            
            Inputs:
            - action_key: action to be executed.
            - action_cb_args: tuple containing optional arguments to the registed action_callback
            
            Outputs:
            - state_key: state resolved after evaluating the transition rule
        
        """
        
        if self.transitions.has_key(action_key):
            
            action_tuple = self.transitions[action_key]
            next_state_key = action_tuple[0]
            action_cb = action_tuple[1]
            condition_cb = action_tuple[2]
            
            if condition_cb():                
                
                action_cb(*action_cb_args)
                return next_state_key
            else:
                return self.key
        else:
            return self.key
        
class StateMachine:
    
    def __init__(self):
        
        self.states_dict={}
        self.active_state_key = None

    def add_state(self,state_obj):
        
        if self.active_state_key == None:
            self.active_state_key = state_obj.key
        
        self.states_dict[state_obj.key] = state_obj               
            
        
    def execute(self,action_key,action_cb_args=()):
        
        
        state_obj = self.states_dict[self.active_state_key]
        next_state_key = state_obj.execute(action_key,action_cb_args)
        
        if self.states_dict.has_key(next_state_key):        
            if next_state_key != self.active_state_key: # transition made
                self.active_state_key = next_state_key
        else:
            print "State Machine has no %s key"%(next_state_key)
            
        return self.active_state_key
        
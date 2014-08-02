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
        self.actions = {} # dictionary of actions (keys) and their corresponding callbacks
        
        
    def add_action(self,action_key,
                       action_cb = lambda: sys.stdout.write("No action callback\n")):
                        # ,condition_cb = lambda: True):
        """
        Adds transition rule to the state
        
        Inputs:
        - action_key: action key for which this transition rule applies
        - next_state_key: state to transition to after action callback is executed.
        - condition_cb: callback that checks a condition and returns either True or False.  When True, the 
            transition will proceed when invoked through the execute() method.  
            If False then execute() will return reject the transition.
            For instance, the callback could potentially check an interval threshold from <0,1> at which the transition
            is permitted
        """
        self.actions[action_key] = action_cb
        
    def has_action(self,action_key):
        
        return self.actions.has_key(action_key)
        
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
            - True/False: True when condition is validated.  False otherwise
        
        """
        
        if self.actions.has_key(action_key):
            
            action_cb = self.actions[action_key]
            action_cb(*action_cb_args)
            #condition_cb = action_tuple[1]
            return True
        else:
            print "Action not supported"
            return False
        
class StateMachine:
    
    def __init__(self):
        
        self.states_dict={}
        self.active_state_key = None
        self.transitions={}

    def add_transition(self,state_obj,action_key,next_state_key,condition_cb):
        
        # inserting as active state if None is currently selected
        if self.active_state_key == None:
            self.active_state_key = state_obj.key            
            
        if self.states_dict.has_key(state_obj.key): 
            
            # transition rules for the state           
            transition_dict = self.transitions[state_obj.key]   
            
            # add (next_state_key,condition_callback) tuple to the list
            if transition_dict.has_key(action_key):
                action_list = transition_dict[action_key]
                action_list.append( (next_state_key,condition_cb))
              
            # create new list for all transitions supported for this action
            # at this state  
            else:
                action_list = [(next_state_key,condition_cb)]
                transition_dict[action_key] = action_list
                
                
            
        else:       
            self.states_dict[state_obj.key] = state_obj
            self.transitions[state_obj.key] = {action_key:[(next_state_key,condition_cb)]}    
            
        
    def execute(self,action_key,action_cb_args=()):
        
        
        if self.transitions.has_key(self.active_state_key):            
            transition_dict = self.transitions[self.active_state_key]
            
            # check if valid transition
            if transition_dict.has_key(action_key):
                
                # go through each rule defined for this action and return true on the first one that validates
                action_list = transition_dict[action_key]
                for action_tuple in action_list:
                    
                    state_key = action_tuple[0]
                    condition_cb = action_key[1]
                
                    # examine condition
                    if condition_cb():
                        state_obj = self.states_dict[state_key]
                        
                        # execute action
                        if state_obj.execute(action_key,action_cb_args):
                            self.active_state_key = state_key
                            return True
                        
                        else:
                            print "Transition failed"
                    
                        #endif
                    
                    else: # condition evaluation failed
                        
                        continue
                
                    #endif
                    
                #endfor
                
            else:
                print "Transition for the %s action at the state %s not supported"%(action_key,self.active_state_key)
                return False
                
            #endif
            
        else:
            print "Transitions from the state %s have not been defined"%(self.active_state_key)
            return False
        
        #endif
        
        return True
        
import sys

class StateKeys:
    
    NONE=""
    STANDING="STANDING"
    WALKING="WALKING"
    JUMPING="JUMPING"
    FALLING="FALLING"
    LANDING="LANDING"
    
class State:
    
    def __init__(self,state_key,exit_cb = None):
        
        self.key = state_key
        self.actions = {} # dictionary of actions (keys) and their corresponding callbacks
        self.exit_callback = exit_cb
        
    def set_exit_callback(self,exit_cb):
        
        self.exit_callback = exit_cb        
        
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
        
    def enter(self,action_key,action_cb_args=()):
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
            print "Action not supported"
            return False
        
    def exit(self):
        
        if self.exit_callback != None:
            self.exit_callback()
        
class StateMachine:
    
    def __init__(self):
        
        self.states_dict={}
        self.active_state_key = None
        self.transitions={}
        self.enter = self.execute  # will be called when used as a sub state machine
        
    def add_state(self,state_obj):
        
        if not self.states_dict.has_key(state_obj.key):
            self.states_dict[state_obj.key] = state_obj
        else:
            self.states_dict[state_obj.key] = state_obj
            print "State was already registered in state machine, new entry will now replace it"

    def add_transition(self,state_obj,action_key,next_state_key,condition_cb = lambda: True):
        
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
                    condition_cb = action_tuple[1]
                
                    # examine condition
                    if condition_cb():
                        next_state_obj = self.states_dict[state_key]
                        active_state_obj = self.states_dict[self.active_state_key]
                        
                        # exiting active state
                        active_state_obj.exit()
                        
                        # setting next state as active
                        self.active_state_key = state_key
                        
                        # calling state enter routine
                        if not next_state_obj.enter(action_key,action_cb_args):
                            
                            # reverting upon failure
                            self.active_state_key = active_state_obj.key                            
                            print "Transition failed"
                            return False                        
                    
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
        
import pygame.event
from simple_platformer.game_state_machine import StateMachineActionKeys
from simple_platformer.game_state_machine import State
       
class StateMachine(object):
    
    class Events:
    
        SUBMACHINE_ACTION = pygame.USEREVENT + 3         
        EVENTS_LIST = [SUBMACHINE_ACTION]   
        
    #static method
    def post_action_event(sm,action_key,event_type):               
        
        if StateMachine.Events.EVENTS_LIST.count(event_type) > 0:                    
            event = pygame.event.Event(event_type,{'notify':lambda : sm.execute(action_key)})
            pygame.event.post(event)
        else:
            print 'ERROR: event type \'%s\' not supported by StateMachine'%(event_type)
        #endif
            
    def __init__(self):
        
        self.states_dict={}
        self.active_state_key = None
        self.transitions={} 

        
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
                
            #endif    
            
        else:       
            self.states_dict[state_obj.key] = state_obj
            self.transitions[state_obj.key] = {action_key:[(next_state_key,condition_cb)]}  
        
        #endif
            
        print "Added transition rule : From %s state : %s action : To %s state"%(state_obj.key,action_key,next_state_key)  
           
        
    def execute(self,action_key,action_cb_args=()):
        
        
        if self.transitions.has_key(self.active_state_key):            
            transition_dict = self.transitions[self.active_state_key]
            
            # check if valid transition
            if transition_dict.has_key(action_key):               

                
                # execute action on active state
                active_state_obj = self.states_dict[self.active_state_key]               
                if active_state_obj.has_action(action_key):
                    active_state_obj.execute(action_key,action_cb_args)
                
                #endif
                
                # go through each rule defined for this action and return true on the first one that validates
                action_list = transition_dict[action_key]  
                
                for action_tuple in action_list:
                    
                    state_key = action_tuple[0]
                    condition_cb = action_tuple[1]
                
                    # examine condition
                    if condition_cb():
                        next_state_obj = self.states_dict[state_key]                       
                        
                        
                        # exiting active state
                        active_state_obj.exit()
                        
                        # entering new state                        
                        next_state_obj.enter()
                        
                        # setting next state as active
                        self.active_state_key = state_key
                        
                        print "Transition from state [%s] : through action [%s] : to state [%s]"%(active_state_obj.key,
                                                                          action_key,
                                                                          self.active_state_key)
                        
                        # calling state enter routine
                        if next_state_obj.execute(action_key,action_cb_args):
                            
                            # transition succeeded

                            return True
                        
                        else: 
                            
                            # reverting upon failure
                            #self.active_state_key = active_state_obj.key                            
                            #print "Transition failed, reverted to state %s from state %s"%(self.active_state_key,state_key)
                            return False                 
                    
                        #endif
                    
                    else: # condition evaluation failed
                        
                        continue
                
                    #endif
                    
                #endfor                
                
            else:
                
                # no transition for this action, check if current state supports action
                active_state_obj = self.states_dict[self.active_state_key]
                if (active_state_obj.has_action(action_key) and 
                    active_state_obj.execute(action_key,action_cb_args)):
                    
                    # executed supported action under current state
                    return True
                else:
                
                    #print "Transition for the %s action at the state %s not supported"%(action_key,self.active_state_key)
                    return False
                #endif
                
            #endif
            
        else:
            print "Transitions from the state %s have not been defined"%(self.active_state_key)
            return False
        
        #endif
        
        return True
    
class SubStateMachine(StateMachine):           
        
    class StateKeys(object):
        
        START = 'SUBMACHINE_START_STATE'
        STOP = 'SUBMACHINE_STOP_STATE'
        NONE = 'NONE'
        
        """
    StartState:
        Internal state of a Submachine used to indicate that the submachine has been entered.
        When this state is reached the 'SUBMACHINE_START' action execution will be scheduled
        in the pygame.event queue.  It should not be used outside the containing Submachine.
    """  
        
    class StartState(State):
        
        def __init__(self,parent_sm):
            
            State.__init__(self,SubStateMachine.StateKeys.START)
            self.parent_sm = parent_sm
            
        def enter(self):    
            print "SM START state entered"   
            self.parent_sm.start()
    
    """
    StopState:
        Internal state of a Submachine used to indicate that the submachine will be exited.
        When this state is reached the 'SUBMACHINE_STOP' action execution will be scheduled
        in the pygame.event queue.  It should not be used outside the containing Submachine.
    """        
            
    class StopState(State):
        
        def __init__(self,parent_sm):
            
            State.__init__(self,SubStateMachine.StateKeys.STOP)
            self.parent_sm = parent_sm
            
        def enter(self):   
            print 'SM STOP state entered'         
            self.parent_sm.stop()
            
    
    def __init__(self,key,parent_sm = None):
        StateMachine.__init__(self)
        
        self.key = key
        self.parent_state_machine = parent_sm
        self.action_list = []
        self.start_state = SubStateMachine.StartState(self)
        self.stop_state = SubStateMachine.StopState(self)  
        
        # adding start and stop sub machine states to transition table
        self.add_transition(self.start_state, StateMachineActionKeys.__IGNORE_ACTION__,
                            SubStateMachine.StateKeys.START, None)
        self.add_transition(self.stop_state, StateMachineActionKeys.__IGNORE_ACTION__,
                    SubStateMachine.StateKeys.STOP, None)
        
        
    def has_action(self,action_key):        
        return (self.action_list.count(action_key) > 0)
        
    @property    
    def action_keys(self):
        return self.action_list
        
    def add_transition(self,state_obj,action_key,next_state_key,condition_cb = lambda: True):
        StateMachine.add_transition(self, state_obj, action_key, next_state_key, condition_cb)
        
        if self.action_list.count(action_key) == 0:
            self.action_list.append(action_key)
        #endif
        
        # adding actions to action list
        action_keys = state_obj.action_keys     
        for akey in action_keys:
            if self.action_list.count(akey) == 0:
                self.action_list.append(akey)
            #endif
        #endfor
        
    def start(self):
        
        if self.parent_state_machine != None:
            StateMachine.post_action_event(self.parent_state_machine,
                                           StateMachineActionKeys.SUBMACHINE_START,
                                            StateMachine.Events.SUBMACHINE_ACTION)
            
    def stop(self):
        
        self.active_state_key = self.start_state.key
        
        if self.parent_state_machine != None:
            StateMachine.post_action_event(self.parent_state_machine,
                                           StateMachineActionKeys.SUBMACHINE_STOP,
                                            StateMachine.Events.SUBMACHINE_ACTION)
        
    def enter(self):        
        
        print "Entering '%s' SubMachine"%(self.key)
        active_state_obj = self.states_dict[self.active_state_key]
        active_state_obj.enter()
        
        
    def exit(self):
        print  "Exiting '%s' SubMachine"%(self.key)
        active_state_obj = self.states_dict[self.active_state_key]
        active_state_obj.exit()
        self.active_state_key = self.start_state.key
        
    
        
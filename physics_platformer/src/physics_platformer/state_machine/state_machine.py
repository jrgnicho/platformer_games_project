#import pygame.event
from physics_platformer.state_machine import StateMachineActionKeys
from physics_platformer.state_machine import State
import logging

class StateEvent(object):
    
    def __init__(self,state_mach,action_key):
        
        self.sm_ = state_mach
        self.action_key_ = action_key
        
    def notify(self,args= ()):
        """
        Executes the action on the state machine
        """
        logging.debug("State event executing %s action"%(self.action_key_))
        self.sm_.execute(self.action_key_,*args)
        

class StateEventHandler(object):
    
    def __init__(self):     
        
        self.events_buffer_ = []
        
    def addEvent(self,evnt,args = ()): 
        
        self.events_buffer_.append((evnt,args))   
        
    def consumeEvents(self):
        
        for tp in self.events_buffer_:
            evnt = tp[0]
            args = tp[1]
            evnt.notify(*args)
            
        # clearing buffer
        self.events_buffer_ = []
        

       
class StateMachine(object):    
     
    __STATE_EVENT_HANDLER__ = StateEventHandler()
    
     ############# Static Methods #################  
    @staticmethod
    def postEvent(evnt,args = ()):
        """
        StateMachine.postEvent(StateEvent evnt, args = () )
        A StateMachineEvent can be posted using the StateMachine.postEvent(...) static method.  In general, it should be used as part of a state's 
        action callback.  For instance when we have the following state and we'd like to respond to an action by executing an action on the containing
        state machine we could do the following:
        my_state = State("MyState")
        my_state.addAction("EXIT_MOVE",lambda args : StateMachine.postEvent(StateEvent(state_machine,'DONE',args) )
        
        Inputs
        - evnt: A StateEvent object
        - args: Optional arguments to be passed to the events notify method
        """
        StateMachine.__STATE_EVENT_HANDLER__.addEvent(evnt, args)     
     
    @staticmethod   
    def processEvents():
        StateMachine.__STATE_EVENT_HANDLER__.consumeEvents()     

            
    def __init__(self):
        
        self.states_dict_={}
        self.active_state_key_ = None
        self.transitions_dict_={} 

        
    def addState(self,state_obj):
        
        if not self.states_dict_.has_key(state_obj.getKey()):
            self.states_dict_[state_obj.getKey()] = state_obj
            self.transitions_dict_[state_obj.getKey()]  = {}
        else:
            self.states_dict_[state_obj.getKey()] = state_obj
            logging.warning( "State '%s'was already registered in state machine, new entry will now replace it" %(state_obj.getKey()))

    def addTransition(self,state_key,action_key,next_state_key,condition_cb = lambda: True):
        """
        addTransition(String state_key, String action_key, String next_state_key, Cb condition_cb =  = lambda: True)
            Adds a transition rule from one state to another when an action is requested.  This transition will take place whenever
            the StateMachine.execute(action_key) method is invoked on the StateMachine object and the state machine is at the state
            indicated by 'state_key'
            
            Inputs:
            - state_key: The state to transition from.
            - action_key: The requested action.
            - next_state_key: The state to transition into
            - condition_cb: (Optional) A callback that returns true or false.  Transition will take place when the callback returns True.
            
            Outpurs:
            - success: Bool
        
        """
        
        # inserting as active state if None is currently selected
        if self.active_state_key_ == None:
            self.active_state_key_ = state_key            
            
        if self.states_dict_.has_key(state_key): 
                        
            # transition rules for the state           
            transition_dict = self.transitions_dict_[state_key]   
            
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
            
            logging.error("State key '%s' was not found"%(state_key))
            return False
        
        #endif
            
        logging.info( "Added transition rule : From %s state : %s action : To %s state"%(state_key,action_key,next_state_key) ) 
        return True           
        
    def execute(self,action_key,action_cb_args=()):
        
        
        if self.transitions_dict_.has_key(self.active_state_key_):            
            transition_dict = self.transitions_dict_[self.active_state_key_]
            
            # check if valid transition
            if transition_dict.has_key(action_key):               

                
                # execute action on active state
                active_state_obj = self.states_dict_[self.active_state_key_]               
                if active_state_obj.hasAction(action_key):
                    active_state_obj.execute(action_key,action_cb_args)
                
                #endif
                
                # go through each rule defined for this action and return true on the first one that validates
                action_list = transition_dict[action_key]  
                
                for action_tuple in action_list:
                    
                    state_key = action_tuple[0]
                    condition_cb = action_tuple[1]
                
                    # examine condition
                    if condition_cb():
                        next_state_obj = self.states_dict_[state_key]                       
                        
                        
                        # exiting active state
                        active_state_obj.exit()
                        
                        # entering new state                        
                        next_state_obj.enter()
                        
                        # setting next state as active
                        self.active_state_key_ = state_key
                        
                        logging.debug("Transition from state [%s] : through action [%s] : to state [%s]"%(active_state_obj.getKey(),
                                                                          action_key,
                                                                          self.active_state_key_))
                        
                        return True
                        
                        # execting action on newly entered state
#                         if next_state_obj.execute(action_key,action_cb_args):
#                             return True                        
#                         else:                             
#                             return False                 
                    
                    
                    else: # condition evaluation failed
                        
                        continue
                               
                
            else:
                
                # no transition for this action, check if current state supports action
                active_state_obj = self.states_dict_[self.active_state_key_]
                if (active_state_obj.hasAction(action_key) and 
                    active_state_obj.execute(action_key,action_cb_args)):
                    
                    # executed supported action under current state
                    return True
                else:
                
                    #print "Transition for the %s action at the state %s not supported"%(action_key,self.active_state_key_)
                    return False
                #endif
                
            #endif
            
        else:
            logging.warning( "Transitions from the state %s have not been defined"%(self.active_state_key_))
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
            self.parent_sm_ = parent_sm
            
        def enter(self):    
            logging.debug( "SM START state entered"   )
            self.parent_sm_.start()
    
    """
    StopState:
        Internal state of a Submachine used to indicate that the submachine will be exited.
        When this state is reached the 'SUBMACHINE_STOP' action execution will be scheduled
        in the pygame.event queue.  It should not be used outside the containing Submachine.
    """        
            
    class StopState(State):
        
        def __init__(self,parent_sm):
            
            State.__init__(self,SubStateMachine.StateKeys.STOP)
            self.parent_sm_ = parent_sm
            
        def enter(self):   
            logging.debug( 'SM STOP state entered')      
            self.parent_sm_.stop()
            
    
    def __init__(self,key,parent_sm = None):        
        """
        Submachine
        Subclasses a state machine. It requires that you add the following transition for entering to the first functional state:
            - addTransition(SubStateMachine.StateKeys.START ,StateMachineActionKeys.SUBMACHINE_START , my_entry_state_key)
        
            It alse requires that you add another transition to exit the state machine:
            - addTransition(my_terminal_state ,StateMachineActionKeys.SUBMACHINE_STOP , SubStateMachine.StateKeys.STOP)
        """
        StateMachine.__init__(self)
        
        self.key_ = key
        self.parent_sm_ = parent_sm
        self.action_list_ = []
        self.start_state_ = SubStateMachine.StartState(self)
        self.stop_state_ = SubStateMachine.StopState(self)  
        
        # adding start and stop sub machine states to transition table
        self.addTransition(self.start_state_, StateMachineActionKeys.__IGNORE_ACTION__,
                            SubStateMachine.StateKeys.START, None)
        self.addTransition(self.stop_state_, StateMachineActionKeys.__IGNORE_ACTION__,
                    SubStateMachine.StateKeys.STOP, None)
        
        
    def hasAction(self,action_key):        
        return (self.action_list_.count(action_key) > 0)        
 
    def getActionKeys(self):
        return seself.action_list_        
    def addTransition(self,state_key ,action_key ,next_state_key,condition_cb = lambda: True):
        StateMachine.addTransition(self, state_key , action_key, next_state_key, condition_cb)
        
        if self.action_list_.count(action_key) == 0:
            self.action_list_.append(action_key)
        #endif
        
        # adding actions to action list
        state_obj = self.states_dict_[state_key]
        action_keys = state_obj.getActionKeys()     
        for akey in action_keys:
            if self.action_list_.count(akey) == 0:
                self.action_list_.append(akey)
            #endif
        #endfor
        
    def start(self):
        
        if self.parent_sm_ != None:
            StateMachine.postEvent(StateEvent(self.parent_sm_, StateMachineActionKeys.SUBMACHINE_START))
            
    def stop(self):
        
        # Set the start state as the active state key before leaving
        self.active_state_key_ = self.start_state_.getKey()
        
        if self.parent_sm_ != None:
            StateMachine.postEvent(StateEvent(self.parent_sm_, StateMachineActionKeys.DONE))
        
    def enter(self):        
        
        logging.debug( "Entering '%s' SubMachine"%(self.getKey()))
        active_state_obj = self.states_dict_[self.active_state_key_]
        active_state_obj.enter()
        
        
    def exit(self):
        logging.debug(  "Exiting '%s' SubMachine"%(self.getKey()))
        active_state_obj = self.states_dict_[self.active_state_key_]
        active_state_obj.exit()
        self.active_state_key_ = self.start_state_.getKey()
        
    
        
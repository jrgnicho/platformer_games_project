#!/usr/bin/env python
from simple_platformer.game_state_machine import *

class ActionExecutor():
    
    def __init__(self):
        
        self.counter = 0
    
    def increment_counter_action(self,val = 1):
        
        print "incremented by %i"%val
        self.counter +=val
        
    def is_counter_greater_than(self,val):
        
        return self.counter > val
        
        

class TestStateMachine(StateMachine):
    
    # custom action keys
    ACTION_INCR_1 = "ACTION_INCR_1"
    ACTION_DECR_2 = "ACTION_DECR_2"
    ACTION_INCR_3 = "ACTION_INCR_3"
    ACTION_INCR_VAL="ACTION_INCR_VAL"
    ACTION_EXIT = "ACTION_EXIT"
    
    # custom state keys
    STATE_A = "STATE_A"
    STATE_B = "STATE_B"
    STATE_C = "STATE_C"
    EXIT = "EXIT"

    
    def __init__(self):
        
        StateMachine.__init__(self)
        
        self.action_exec_ = ActionExecutor()
        self.proceed = True
        
    def exit(self):
        
        print "exiting"
        self.proceed = False
        
        
    def create_rules(self):
        
        ################################### Creating rules ############################
        
        # rule 1
        st = State(TestStateMachine.STATE_A)
        st.add_action(TestStateMachine.ACTION_INCR_3,lambda : self.action_exec_.increment_counter_action(3))
        st.add_action(TestStateMachine.ACTION_INCR_1,lambda: self.action_exec_.increment_counter_action(1))
        st.add_action(TestStateMachine.ACTION_DECR_2,lambda: self.action_exec_.increment_counter_action(-2))
        
        
        self.add_transition(st,TestStateMachine.ACTION_EXIT, TestStateMachine.EXIT,
                            lambda: self.action_exec_.is_counter_greater_than(9))
        self.add_transition(st,TestStateMachine.ACTION_INCR_1, TestStateMachine.STATE_B,
                            lambda: self.action_exec_.is_counter_greater_than(-1))
        self.add_transition(st,TestStateMachine.ACTION_DECR_2, TestStateMachine.STATE_C,
                            lambda: self.action_exec_.is_counter_greater_than(4))  
        self.add_transition(st,TestStateMachine.ACTION_INCR_VAL, TestStateMachine.STATE_C,
                    lambda: self.action_exec_.is_counter_greater_than(4))       
        
        
        
        # rule 2
        st = State(TestStateMachine.STATE_B)        
        st.add_action(TestStateMachine.ACTION_DECR_2,lambda: self.action_exec_.increment_counter_action(-2))
        st.add_action(TestStateMachine.ACTION_INCR_1,lambda: self.action_exec_.increment_counter_action(1))
        st.add_action(TestStateMachine.ACTION_INCR_VAL,self.action_exec_.increment_counter_action)
        
        self.add_transition(st,TestStateMachine.ACTION_INCR_1, TestStateMachine.STATE_C,
                            lambda: self.action_exec_.is_counter_greater_than(0))
        self.add_transition(st,TestStateMachine.ACTION_INCR_3, TestStateMachine.STATE_A,
                            lambda: self.action_exec_.is_counter_greater_than(6))  
        self.add_transition(st,TestStateMachine.ACTION_EXIT, TestStateMachine.EXIT,
                            lambda: self.action_exec_.is_counter_greater_than(9))      
        
        
        # rule 3
        st = State(TestStateMachine.STATE_C)
        st.add_action(TestStateMachine.ACTION_DECR_2,lambda: self.action_exec_.increment_counter_action(-2))
        st.add_action(TestStateMachine.ACTION_INCR_1,lambda: self.action_exec_.increment_counter_action(1))
        st.add_action(TestStateMachine.ACTION_INCR_VAL,lambda x:self.action_exec_.increment_counter_action(x))
        
        self.add_transition(st,TestStateMachine.ACTION_INCR_3, TestStateMachine.STATE_B,
                            lambda: self.action_exec_.is_counter_greater_than(6))  
        self.add_transition(st,TestStateMachine.ACTION_INCR_3, TestStateMachine.STATE_A) 
        self.add_transition(st,TestStateMachine.ACTION_DECR_2, TestStateMachine.STATE_B,lambda:self.action_exec_.is_counter_greater_than(10)) 
        self.add_transition(st,TestStateMachine.ACTION_EXIT, TestStateMachine.EXIT,
                            lambda: self.action_exec_.is_counter_greater_than(9))   
        
        st = State(TestStateMachine.EXIT)
        st.add_action(TestStateMachine.ACTION_EXIT,lambda: self.exit())
        self.add_state(st)

        
    def execute(self,action_key,args=()):
        
        if self.proceed:
        
            prev_state_key = self.active_state_key
            
            StateMachine.execute(self,action_key,args)
            
            print "State Machine transitioned from %s : %s : %s, counter value = %i"%(
                prev_state_key,action_key,self.active_state_key,self.action_exec_.counter)
            
        
    def run(self):
        
        counter = 0
        while(self.proceed and (counter < 4)    ):
            
            self.execute(TestStateMachine.ACTION_INCR_1) 
            self.execute(TestStateMachine.ACTION_EXIT)  
            self.execute(TestStateMachine.ACTION_INCR_1)              
            self.execute(TestStateMachine.ACTION_INCR_3)        
            self.execute(TestStateMachine.ACTION_INCR_VAL,[7])
            self.execute(TestStateMachine.ACTION_DECR_2)
            
            counter+=1
            
if __name__=="__main__":
    
    sm = TestStateMachine()
    sm.create_rules()    
    sm.run()
        
        
        
        
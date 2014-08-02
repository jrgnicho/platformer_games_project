#!/usr/bin/env python
import roslib
import smach

# define state Foo
class Foo(smach.State):
    def __init__(self,outcomes=['outcome1','outcome2']):
        smach.State.__init__(self, outcomes)
        self.counter = 0

    def execute(self, userdata):
        print('Executing state FOO')
        if self.counter < 3:
            self.counter += 1
            return 'outcome1'
        else:
            return 'outcome2'


# define state Bar
class Bar(smach.State):
    def __init__(self,outcomes=['outcome2']):
        smach.State.__init__(self, outcomes)

    def execute(self, userdata):
        print('Executing state BAR')
        return 'outcome2'
    
# define state Bas
class Bas(smach.State):
    def __init__(self,outcomes=['outcome3']):
        smach.State.__init__(self, outcomes)
        self.executed_once = False

    def execute(self, userdata):
        
        print('Executing state BAS')
        if self.executed_once:
            return "outcome1"
        else:
            self.executed_once = True
            return 'outcome3'
        



# main
def main():
    #rospy.init_node('smach_example_state_machine')

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['outcome4', 'outcome5'])
    sm_sub = smach.StateMachine(outcomes=['outcome4',"outcome8"])
    
    with sm_sub:
        
        smach.StateMachine.add('BAS',Bas(outcomes=['outcome3','outcome1']),
                               transitions={"outcome3":"outcome4",
                                            "outcome1":"outcome8"})

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('FOO', Foo(outcomes=['outcome1','outcome2']), 
                               transitions={'outcome1':'BAR', 
                                            'outcome2':'SUB'})
        smach.StateMachine.add('BAR', Bar(outcomes=['outcome2']), 
                               transitions={'outcome2':'FOO'})
        
        smach.StateMachine.add('SUB',sm_sub,
                               transitions={"outcome4":"BAR",
                                            "outcome8":"outcome5"})

    # Execute SMACH plan
    print "=============== Second SM run ========================="
    outcome = sm.execute()
    
    print "=============== Second SM run ========================="
    outcome = sm.execute()


if __name__ == '__main__':
    main()
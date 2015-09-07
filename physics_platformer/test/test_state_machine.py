#!/usr/bin/env python
import logging
import sys

from pandac.PandaModules import * 
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpFunc
from direct.task.TaskManagerGlobal import taskMgr
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.controls.InputState import InputState

from physics_platformer.state_machine import Action
from physics_platformer.state_machine import State
from physics_platformer.state_machine import StateMachine
from physics_platformer.state_machine import StateEvent
from physics_platformer.state_machine import StateMachineActions


PLAY_TASK_DELAY = 2.0
INPUT_DELAY = 1.0

# actions
PLAY_ACTION = Action('PLAY')
LOOP_ACTION = Action('LOOP')
MONITOR_ACTION = Action('MONITOR')
DONE_ACTION= Action('DONE')
EXIT_ACTION = Action('EXIT')
VERBOSE = Action('PRINT_VERBOSITY')

# states
PLAYING_STATE = 'PLAYING'
LOOPING_STATE = 'LOOPING'
IDLED_STATE = 'IDLED'
MONITORING_STATE = 'MONITORING'

# hiding window
#ConfigVariableString("window-type","none").setValue("none") 

class InputAction(Action):
    
  def __init__(self,key,direction):
    Action.__init__(self,key)
    self.direction = direction
    

PRINT_DIRECTION_ACTION = InputAction('PRINT_DIRECTION','None')

class LoopState(State):
    
    def __init__(self):
        State.__init__(self,LOOPING_STATE)
        self.seq_ = None
        
    def enter(self):
        
        self.seq_ = Sequence()
        self.seq_.append(LerpFunc(self.loopFunc,fromData = 0,toData = 20, duration = 4))
        self.seq_.loop()
    
    def exit(self):              
        self.seq_.finish()
        
    def loopFunc(self,t):        
        logging.info("Looping state t = %f, press 'd' to exit"%t)
        
class PlayState(State):
    
    def __init__(self,parent_sm):
        
        State.__init__(self,PLAYING_STATE)
        self.elapsed_ = 0
        self.task_ = None
        self.parent_sm_ = parent_sm
        
    def enter(self):      
        self.elapsed_ = 0  
        self.task_ = taskMgr.add(self.playTaskCallback,'PlayFunction')
        
    def exit(self):
        taskMgr.remove(self.task_)           
        if self.elapsed_ < PLAY_TASK_DELAY:
            logging.info("Exited task early after %f seconds instead of %f"%(self.elapsed_,PLAY_TASK_DELAY))    
        else:
            logging.info("Exited task at %f seconds"%(self.elapsed_))        
        
        
    def playTaskCallback(self,task):
        
        self.elapsed_ = task.time
        if task.time < PLAY_TASK_DELAY:
            logging.info("Play task time elapsed %f, press 'd' to exit"%(task.time))
            return task.cont
        else:
            logging.debug('Play State posting event with %s_action'%(DONE_ACTION))
            StateMachine.postEvent(StateEvent(self.parent_sm_, DONE_ACTION))
            return task.done    
          
          
class MonitorState(State):         
  
  def __init__(self):
    
    State.__init__(self,MONITORING_STATE)
    self.addAction(PRINT_DIRECTION_ACTION.key,self.printDirection)    
    
  def printDirection(self,action):
    logging.info('Direction %s pressed'%(action.direction))
    
          
    

class TestStateMachine(ShowBase):
    
    def __init__(self):
        
        ShowBase.__init__(self)
        self.setupInput()
        self.setupStates()
        
        taskMgr.add(self.update,"update")
        
    def update(self,task):
        self.processInput(task)  
        StateMachine.processEvents()  
        
        return task.cont
        
    def setupInput(self):
        
        # Inputs (Polling)
        self.input_state_ = InputState()
        self.input_state_.watchWithModifiers("right","arrow_right")
        self.input_state_.watchWithModifiers('left', 'arrow_left')
        self.input_state_.watchWithModifiers('up', 'arrow_up')
        self.input_state_.watchWithModifiers('down', 'arrow_down')
        
        # state transition presses
        self.input_state_.watchWithModifiers('verbose',"v")
        self.input_state_.watchWithModifiers('monitor',"m")
        self.input_state_.watchWithModifiers("loop",'l')
        self.input_state_.watchWithModifiers("play",'p')
        self.input_state_.watchWithModifiers("done",'d')
        self.input_state_.watchWithModifiers("exit",'escape')
        
    def setupStates(self):
        
        self.state_machine_ = StateMachine()        
        sm = self.state_machine_
        
        # creating states   
        
        idle_state = State(IDLED_STATE)
        idle_state.setEntryCallback(self.printIdleInstructions)
        idle_state.setExitCallback(lambda: logging.info("Exited Idled State"))  
        idle_state.addAction(VERBOSE.key,self.printTaskVerbose)
        idle_state.addAction(EXIT_ACTION.key,self.exitCallback) 
        sm.addState(idle_state)
             
        
        monitor_state = MonitorState()
        monitor_state.setEntryCallback(lambda : logging.info("""
            Press an arrow
            Press 'd' to exit the state
        """))
        #monitor_state.addAction(PRINT_DIRECTION_ACTION.key,lambda d : logging.info('Direction %s pressed'%(d)))
        sm.addState(monitor_state)
        
        loop_state = LoopState()
        loop_state.addAction(VERBOSE.key,self.printTaskVerbose)
        sm.addState(loop_state)
        
        play_state = PlayState(self.state_machine_)   
        play_state.addAction(VERBOSE.key,self.printTaskVerbose) 
        sm.addState(play_state)
        
        # creating transitions
        
        sm.addTransition(IDLED_STATE,LOOP_ACTION.key,LOOPING_STATE)
        sm.addTransition(IDLED_STATE,PLAY_ACTION.key,PLAYING_STATE)
        sm.addTransition(IDLED_STATE,MONITOR_ACTION.key,MONITORING_STATE)
        
        sm.addTransition(PLAYING_STATE,DONE_ACTION.key,IDLED_STATE)
        
        sm.addTransition(LOOPING_STATE,DONE_ACTION.key,IDLED_STATE)
        
        sm.addTransition(MONITORING_STATE,DONE_ACTION.key,IDLED_STATE)      
        
        self.printIdleInstructions()        
        
        
    def printTaskVerbose(self,action):                
        logging.info(str(taskMgr))
        
    def printIdleInstructions(self):
        
        logging.info(
                     """
                     Press 'l' to go into the Looping State
                     Press 'p' to go into the Playing State
                     Press 'm' to go into the Monitor State
                     Press 'ESC' to Exit 
                     """)
        
    def processInput(self,task):

        
        self.input_delay_accum_  = 0
        
        # check directions
        if self.input_state_.isSet('right'): 
          PRINT_DIRECTION_ACTION.direction = 'RIGHT'
          self.state_machine_.execute(PRINT_DIRECTION_ACTION,['RIGHT'])
    
        if self.input_state_.isSet('left'): 
          PRINT_DIRECTION_ACTION.direction = 'LEFT'
          self.state_machine_.execute(PRINT_DIRECTION_ACTION,['LEFT'])
    
        if self.input_state_.isSet('up'): 
          PRINT_DIRECTION_ACTION.direction = 'UP'
          self.state_machine_.execute(PRINT_DIRECTION_ACTION,['UP'])
    
        if self.input_state_.isSet('down'): 
          PRINT_DIRECTION_ACTION.direction = 'DOWN'
          self.state_machine_.execute(PRINT_DIRECTION_ACTION,['DOWN'])
        
        # check transitions
        if self.input_state_.isSet('monitor'): 
          self.state_machine_.execute(MONITOR_ACTION)
    
        if self.input_state_.isSet('loop'): 
          self.state_machine_.execute(LOOP_ACTION)
    
        if self.input_state_.isSet('play'): 
          self.state_machine_.execute(PLAY_ACTION)
    
        if self.input_state_.isSet('done'): 
          self.state_machine_.execute(DONE_ACTION)
          
        if self.input_state_.isSet('verbose'): 
          self.state_machine_.execute(VERBOSE)
          
          
        if self.input_state_.isSet('exit'): 
          self.state_machine_.execute(EXIT_ACTION)
          
        
          
          
        
    def exitCallback(self,action):
        sys.exit(0)
        

if __name__ == '__main__':
    
    log_level = logging.DEBUG
    logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
    
    t = TestStateMachine()    
    t.run()   
        
        
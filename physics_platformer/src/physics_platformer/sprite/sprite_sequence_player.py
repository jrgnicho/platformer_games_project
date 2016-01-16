from direct.interval.IntervalGlobal import Sequence
from panda3d.core import SequenceNode
from direct.interval.IntervalGlobal import Func
from direct.interval.FunctionInterval import Wait
import logging

class SpriteSequencePlayer(SequenceNode):
  
  def __init__(self,name):
    SequenceNode.__init__(self,name)
    self.play_sequence_ = None  # shows each frame during its alloted time.
    self.frame_times_ = [] # contains the time in seconds that each frame is shown
    self.playing_ = False
    
  def __setupSequence__(self,start_frame, end_frame):
    self.__cleanupSequence__()
    self.play_sequence_ = Sequence()  
    
    if start_frame > self.getNumFrames()-1:
      logging.error("start_frame > num_frames - 1")
      return False
    
    if end_frame > self.getNumFrames()-1:
      logging.error("end_frame > num_frames - 1")
      return False
    
    for i in range(start_frame,end_frame+1):
      self.play_sequence_.append(Func(self.pose,i))
      self.play_sequence_.append(Wait(self.frame_times_[i]))
      
    logging.info("Sequence animation %s with times %s"%(self.getName(),str(self.frame_times_[start_frame:end_frame+1])))
      
    return True

  def __cleanupSequence__(self):
    if self.play_sequence_ is not None:
      self.play_sequence_.finish()
      self.play_sequence_ = None
    self.playing_ = False
      
      
  def play(self,from_frame,to_frame):
    
    if self.__setupSequence__(from_frame, to_frame):
      self.play_sequence_.append(Func(self.__cleanupSequence__))      
      self.play_sequence_.start()
      self.playing_ = True
    
  def loop(self,restart,from_frame , to_frame):
    
    if self.__setupSequence__(from_frame, to_frame):
      self.play_sequence_.loop()
      self.playing_ = True
    
  def stop(self):
    self.__cleanupSequence__()
    
  def isPlaying(self):
    return self.playing_
    
  def addFrame(self,card_frame, sort, frame_time):
    '''
    addFrame(Card card_frame, int sort, double frame_time)
    @param card_frame: An instance of the CardMaker class containing the image frame
    @param sort: The index of the frame 
    @param frame_time: The time in seconds that the frame will be shown
    '''
    self.addChild(card_frame,sort)
    self.frame_times_.append(frame_time)
    
    
    
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import PosInterval, Func, Wait
from direct.interval.LerpInterval import LerpPosInterval
from panda3d.core import Vec3, NodePath
import logging



class CameraController(NodePath):
  
  __TRACKING_SPEED__ = 4.0 # meters/second
  __TRACKING_RADIUS__ = 1.0
  
  def __init__(self,camera_np, name = "CameraController"):
    NodePath.__init__(self,name)
    
    self.target_np_ = None
    self.sequence_ = None
    self.camera_np_ = camera_np
    self.target_tracker_np_ = self.attachNewNode("TargetTrackerNode") 
    self.enabled_ = True  
    self.smoothing_ = False
    self.offset_pos_ = Vec3.zero()
    
  def setEnabled(self,enable):
    self.enabled_ = enable
    
    if enable:
      self.__activate__()
    else:
      self.__deactivate__()
      
  def setTargetNode(self, target_np, offset = Vec3.zero()):    
    self.target_np_ = target_np  
    self.target_tracker_np_.setFluidPos(target_np.getPos())
    self.offset_pos_ = offset
    
    if self.enabled_:
      self.__activate__()
      
  def __activate__(self):
    self.camera_np_.reparentTo(self.target_tracker_np_)
    self.camera_np_.setPos(self.offset_pos_)
    
    logging.debug("Activated Camera Controller with offset position " + str(self.offset_pos_))
      
  def __deactivate__(self):
    self.camera_np_.detachNode()
    
  def update(self,dt):
    
    if not self.enabled_:
      return
    
    if self.target_np_ is None:
      return
    
    
    if self.sequence_ is None:
      
      tracker_pos = self.target_tracker_np_.getPos()
      target_pos= self.target_np_.getPos()
      distance = (target_pos - tracker_pos).length()
      
      # check if target is inside traking radious
      if distance > CameraController.__TRACKING_RADIUS__:
        self.__startMotionInterpolation__()
      else:
         self.target_tracker_np_.setFluidPos(target_pos)
    
    
  def __startMotionInterpolation__(self):
    
    start_pos = self.target_tracker_np_.getPos()
    end_pos= self.target_np_.getPos()
    time_ = (end_pos - start_pos).length()/CameraController.__TRACKING_SPEED__
    pos_interval = LerpPosInterval(self.target_tracker_np_, time_, end_pos, startPos=start_pos,
                                   other=None,
                                   blendType='easeOut',
                                   bakeInStart=1,
                                   fluid=1) 
    self.sequence_ = Sequence()
    self.sequence_.append(pos_interval)
    self.sequence_.append(Func(self.__checkTargetPosition__))
    self.sequence_.start()
    logging.info("Started Camera motion Interpolation with time %f",time_)
    
  def __checkTargetPosition__(self):
    distance = (self.target_np_.getPos() - self.target_tracker_np_.getPos()).length()
    
    if distance < 0.001:
      self.__stopMotionInterpolation__()
    else:
      self.__startMotionInterpolation__()
    
  def __stopMotionInterpolation__(self):
    self.sequence_.finish()
    self.sequence_ = None
    logging.info("Finished Camera motion Interpolation")
    
  
    
    
  
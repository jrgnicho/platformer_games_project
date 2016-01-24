from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import PosInterval, Func, Wait
from direct.interval.LerpInterval import LerpPosInterval
from panda3d.core import Vec3, NodePath
import logging



class CameraController(NodePath):
  
  __TRACKING_SPEED__ = 4.0 # meters/second
  __TRACKING_RADIUS__ = 1.0
  __MAX_INTERPOLATION_TIME__ = 0.5
  __CAMERA_POS_OFFSET__ = Vec3(0,-24,4)
  __CAMERA_ORIENT_OFFSET__ = Vec3(0,-5,0)
  
  def __init__(self,camera_np, name = "CameraController"):
    NodePath.__init__(self,name)
    
    self.target_np_ = None
    self.sequence_ = None
    self.camera_np_ = camera_np
    self.target_tracker_np_ = self.attachNewNode("TargetTrackerNode") 
    self.enabled_ = True  
    self.smoothing_ = False
    
  def setEnabled(self,enable):
    self.enabled_ = enable
    
    if enable:
      self.__activate__()
    else:
      self.__deactivate__()
      
  def setTargetNode(self, target_np):    
    self.target_np_ = target_np  
    self.target_tracker_np_.setFluidPos(target_np.getPos())
    
    if self.enabled_:
      self.__activate__()
      
  def __activate__(self):
    self.camera_np_.reparentTo(self.target_tracker_np_)
    self.camera_np_.setPos(CameraController.__CAMERA_POS_OFFSET__)
    self.camera_np_.setHpr(CameraController.__CAMERA_ORIENT_OFFSET__)
    
    logging.debug("Activated Camera Controller for cam %s with local pos %s and hpr %s"%(str(self.camera_np_),
                                                                                         str(self.camera_np_.getPos()),
                                                                                         str(self.camera_np_.getHpr())) )
      
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
    time_ = time_ if time_ < CameraController.__MAX_INTERPOLATION_TIME__ else CameraController.__MAX_INTERPOLATION_TIME__
    
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
    
  
    
    
  
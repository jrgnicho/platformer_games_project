from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import PosInterval, Func, Wait
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from panda3d.core import Vec3, NodePath
import logging

class CameraController(NodePath):
  
  __TRACKING_SPEED__ = 4.0 # meters/second
  __TRACKING_RADIUS__ = 1.0
  __MAX_POS_INTERPOLATION_TIME__ = 0.5
  __ROTATION_INTERPOLATION_TIME__ = 0.6
  __CAMERA_POS_OFFSET__ = Vec3(0,-24,4)
  __CAMERA_ORIENT_OFFSET__ = Vec3(0,-5,0)
  
  def __init__(self,camera_np, name = "CameraController"):
    NodePath.__init__(self,name)
    
    self.target_np_ = None
    self.pos_interpolation_sequence_ = None
    self.camera_np_ = camera_np
    self.target_tracker_np_ = self.attachNewNode("TargetTrackerNode") 
    self.enabled_ = True  
    self.smoothing_ = False
    self.target_ref_np_ = None
    
    # rotation tracking
    self.rot_target_hpr_ = Vec3.zero()
    self.rot_interpolation_sequence_ = Sequence()
    
  def setEnabled(self,enable):
    self.enabled_ = enable
    
    if enable:
      self.__activate__()
    else:
      self.__deactivate__()
      
  def setTargetNode(self, target_np):    
    self.target_np_ = target_np  
    self.target_tracker_np_.setFluidPos(target_np.getPos())
    self.target_tracker_np_.setHpr(target_np,Vec3(0,0,0))
    
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
    
    self.__checkRotationTarget__()
    
    if self.pos_interpolation_sequence_ is None:
      
      ref_np = self.target_np_.getReferenceNodePath()
      tracker_pos = self.target_tracker_np_.getPos(ref_np)
      target_pos= self.target_np_.getPos(ref_np)
      distance = (target_pos - tracker_pos).length()     

      
      # check if target is inside traking radious
      if distance > CameraController.__TRACKING_RADIUS__:
        self.__startPositionInterpolation__()
      else:
         self.target_tracker_np_.setFluidPos(ref_np,target_pos)
    
    
  def __startPositionInterpolation__(self):
    
    start_pos = self.target_tracker_np_.getPos()
    end_pos= self.target_np_.getPos()
    time_ = (end_pos - start_pos).length()/CameraController.__TRACKING_SPEED__
    time_ = time_ if time_ < CameraController.__MAX_POS_INTERPOLATION_TIME__ else CameraController.__MAX_POS_INTERPOLATION_TIME__
    
    pos_interval = LerpPosInterval(self.target_tracker_np_, time_, end_pos, startPos=start_pos,
                                   other=None,
                                   blendType='easeOut',
                                   bakeInStart=1,
                                   fluid=1) 
    self.pos_interpolation_sequence_ = Sequence()
    self.pos_interpolation_sequence_.append(pos_interval)
    self.pos_interpolation_sequence_.append(Func(self.__checkTargetPosition__))
    self.pos_interpolation_sequence_.start()
    logging.info("Started Camera motion Interpolation with time %f",time_)
    
  def __checkTargetPosition__(self):
    distance = (self.target_np_.getPos() - self.target_tracker_np_.getPos()).length()
    
    if distance < 0.001:
      self.__stopPositionInterpolation__()
    else:
      self.__startPositionInterpolation__()
    
  def __stopPositionInterpolation__(self):
    self.pos_interpolation_sequence_.finish()
    self.pos_interpolation_sequence_ = None
    logging.info("Finished Camera motion Interpolation")
    
  def __startRotationInterpolation__(self):
    
    ref_np = self.target_np_.getReferenceNodePath()
    start_hpr = self.target_tracker_np_.getHpr(ref_np)
    end_hpr = self.target_np_.getHpr(ref_np)
    time = CameraController.__ROTATION_INTERPOLATION_TIME__
      
    
    rot_interval = LerpHprInterval(self.target_tracker_np_, time, end_hpr, startHpr = start_hpr,
                                   startQuat = None,
                                   other=ref_np,
                                   blendType='easeIn',
                                   bakeInStart=1,
                                   fluid=0)

      # saving target
    self.rot_target_hpr_ = self.target_np_.getHpr(self.target_np_.getParent())
    current_hpr = self.target_tracker_np_.getHpr(self.target_np_.getParent())
    logging.debug("Camera Interpolated Rotation from %s to %s "%(str(current_hpr),str(self.rot_target_hpr_)))    
        
    # creating sequence
    self.rot_interpolation_sequence_ = Sequence()
    self.rot_interpolation_sequence_.append(rot_interval)
    self.rot_interpolation_sequence_.start()
    
    
  def __checkRotationTarget__(self):
    ref_np = self.target_np_.getParent()
    current_hpr = self.target_np_.getHpr(ref_np)
    diff = abs(current_hpr.getX() - self.rot_target_hpr_.getX())
    if diff > 1e-4 and diff < 360:
      # target changed
      self.__stopRotationInterpolation__()
      self.__startRotationInterpolation__()
      
  def __stopRotationInterpolation__(self):
    if self.rot_interpolation_sequence_ is not None:
      self.rot_interpolation_sequence_.finish()
      self.rot_interpolation_sequence_ = None
    
  
    
    
  
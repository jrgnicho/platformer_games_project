from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import PosInterval, Func, Wait
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from panda3d.core import Vec3, NodePath
import logging
from math import sin,cos, atan2

class CameraController(NodePath):
  
  __TRACKING_SPEED__ = 4.0      # meters/second
  __TRACKING_RADIUS_MIN__ = 0.2
  __TRACKING_RADIUS_MAX__ = 0.5
  __CHASE_TARGET_TIME__ = 0.4
  __MIN_LOCKING_SPEED__ = 1.0   # unist/second
  __MIN_CHASE_SPEED__ = 2.5     # units/second
  
  __ROTATION_INTERPOLATION_TIME__ = 0.6
  __CAMERA_POS_OFFSET__ = Vec3(0,-24,4)
  __CAMERA_ORIENT_OFFSET__ = Vec3(0,-5,0)
  
  def __init__(self,camera_np, name = "CameraController"):
    NodePath.__init__(self,name)
    
    self.target_np_ = None    
    self.camera_np_ = camera_np
    self.target_tracker_np_ = self.attachNewNode("TargetTrackerNode") 
    self.enabled_ = True  
    self.smoothing_ = False
    self.target_ref_np_ = None
    
    # position tracking
    self.target_locked_ = True
    
    # rotation tracking
    self.rot_pr_target_ = Vec3.zero()
    self.rot_interpolation_sequence_ = Sequence()
    
    # time checks
    self.elapsed_time_ = 0 # elapsed time since last update
    
  def setEnabled(self,enable):
    self.enabled_ = enable
    
    if enable:
      self.__activate__()
    else:
      self.__deactivate__()
      
  def setTargetNode(self, target_np):    
    self.target_np_ = target_np  
    self.target_tracker_np_.setPos(target_np.getPos())
    self.target_tracker_np_.setHpr(target_np,Vec3(0,0,0))
    self.target_locked_ = True
    
    if self.enabled_:
      self.__activate__()
      
  def __activate__(self):
    self.camera_np_.reparentTo(self.target_tracker_np_)
    self.camera_np_.setPos(CameraController.__CAMERA_POS_OFFSET__)
    self.camera_np_.setHpr(CameraController.__CAMERA_ORIENT_OFFSET__)
    self.elapsed_time_ = 0.0
    
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
    
    self.__checkRotationTarget__(dt)
    self.__checkPositionTarget__(dt)
    
  def __checkPositionTarget__(self,dt):
    
    
    # computing distances and directions
    ref_np = self.target_np_.getReferenceNodePath()
    target_pos = self.target_np_.getPos(ref_np)
    tracker_pos= self.target_tracker_np_.getPos(ref_np) 
    direction = target_pos - tracker_pos 
    distance = direction.length()   
    norm_direction = direction/distance  
    
    if distance < 1e-6:
      return 
    
    if self.target_locked_:  
      
      if distance > CameraController.__TRACKING_RADIUS_MIN__ and distance < CameraController.__TRACKING_RADIUS_MAX__:       
                    
        r = CameraController.__TRACKING_RADIUS_MIN__   
            
        delta_pos = (norm_direction)*(distance - r)
        self.target_tracker_np_.setPos(ref_np,tracker_pos + delta_pos)
        
      elif distance <= CameraController.__TRACKING_RADIUS_MIN__:
        # smoothly move to target pos
        delta = dt*CameraController.__MIN_LOCKING_SPEED__/2
        delta = delta if delta < distance else distance 
        
        self.target_tracker_np_.setPos(ref_np,tracker_pos + (norm_direction * delta))
      
      elif distance >= CameraController.__TRACKING_RADIUS_MAX__:
        self.target_locked_ = False
        
    
    if not self.target_locked_:  
      if distance > CameraController.__TRACKING_RADIUS_MAX__ : 
        
        speed = distance/CameraController.__CHASE_TARGET_TIME__
        speed = speed if speed > CameraController.__MIN_CHASE_SPEED__ else CameraController.__MIN_CHASE_SPEED__
        delta_pos = norm_direction*(dt*speed)
        self.target_tracker_np_.setPos(ref_np,tracker_pos + delta_pos)
        
      else:
        # smoothly move to target pos
        speed = distance/CameraController.__CHASE_TARGET_TIME__
        speed = speed if speed > CameraController.__MIN_LOCKING_SPEED__ else CameraController.__MIN_LOCKING_SPEED__
        delta = dt*speed
        delta = delta if delta < distance else distance
        self.target_tracker_np_.setPos(ref_np,tracker_pos + (norm_direction * delta))
        
      if distance <= CameraController.__TRACKING_RADIUS_MIN__ :
        self.target_locked_ = True
    
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
    self.rot_pr_target_ = self.target_np_.getHpr(self.target_np_.getParent())
    current_hpr = self.target_tracker_np_.getHpr(self.target_np_.getParent())
    logging.debug("Camera Interpolated Rotation from %s to %s "%(str(current_hpr),str(self.rot_pr_target_)))    
        
    # creating sequence
    self.rot_interpolation_sequence_ = Sequence()
    self.rot_interpolation_sequence_.append(rot_interval)
    self.rot_interpolation_sequence_.start()
    
    
  def __checkRotationTarget__(self,dt):
    ref_np = self.target_np_.getParent()
    current_hpr = self.target_np_.getHpr(ref_np)
    diff = abs(current_hpr.getX() - self.rot_pr_target_.getX())
    if diff > 1e-4 and diff < 360:
      # target changed
      self.__stopRotationInterpolation__()
      self.__startRotationInterpolation__()
      
  def __stopRotationInterpolation__(self):
    if self.rot_interpolation_sequence_ is not None:
      self.rot_interpolation_sequence_.finish()
      self.rot_interpolation_sequence_ = None
    
  
    
    
  
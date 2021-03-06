from platformer_core.game_object import GameObject
from platformer_core.sprite import SpriteAnimator
from platformer_core.animation import AnimationActor
from panda3d.core import BitMask16, LColor, Material
from panda3d.core import Vec3
from panda3d.core import TransparencyAttrib
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func
import logging


class AnimationSpriteAlignment(object):
    
    TOP_ALIGN = BitMask16.bit(0)
    BOTTOM_ALIGN = BitMask16.bit(1)
    LEFT_ALIGN = BitMask16.bit(2)
    RIGHT_ALIGN = BitMask16.bit(3)    
    CENTER_ALIGN_HORIZONTAL = BitMask16.bit(4)   
    CENTER_ALIGN_VERTICAL = BitMask16.bit(5)  
    CENTER_OFFSET_ALIGN = BitMask16.bit(6)
    
    TOP_RIGHT_ALIGN = TOP_ALIGN | RIGHT_ALIGN
    TOP_LEFT_ALIGN = TOP_ALIGN | LEFT_ALIGN
    TOP_CENTER_ALIGN = TOP_ALIGN | CENTER_ALIGN_HORIZONTAL
    BOTTOM_RIGHT_ALIGN = BOTTOM_ALIGN | RIGHT_ALIGN
    BOTTOM_LEFT_ALIGN = BOTTOM_ALIGN | LEFT_ALIGN
    BOTTOM_CENTER_ALIGN = BOTTOM_ALIGN | CENTER_ALIGN_HORIZONTAL
    

class AnimatableObject(GameObject):
    
    def __init__(self,name,size,mass):
        GameObject.__init__(self,name)
        super(AnimatableObject,self).__initToBox__(name,size,mass,False) # initialize game object to a box with no Visual
        self.setTransparency(TransparencyAttrib.M_alpha)
        self.node().setAngularFactor((0,0,0))  # no rotation
        self.animation_root_np_ = self.attachNewNode('animations_root')
        self.animation_root_np_.setPos(Vec3(0,0,-0.5*size.getZ()))
        self.animators_ = {}
        self.selected_animation_name_ = ''
        self.animator_np_ = None # selected animator NodePath
        self.animator_ = None     
        
        # make sprites brigntess consistent 
        material = Material(name + 'animation-material')
        material.setEmission(LColor(1,1,1,1))
        self.animation_root_np_.setMaterial(material)     
        
        # callbacks
        self.frame_monitor_seq_ = Sequence() # Used to monitor animation frames and invoke callbacks
        self.animation_end_cb_ = None
        self.animation_start_cb_ = None
        
    def setObjectID(self,id):
      GameObject.setObjectID(self,id)    
      for k in list(self.animators_.keys()):
        animator = self.animators_[k].node().getPythonTag(SpriteAnimator.__name__) 
        animator.setPythonTag(GameObject.ID_PYTHON_TAG,id) 
        
    # ============ Render Effect Methods ========= #    
    def setViewingNode(self, viewing_node):
      '''
      setViewingNode(NodePath viewing_node)
      @param viewing_node changes orientation so that it is always visible by the viewing node
      '''    
      self.animation_root_np_.setCompass(viewing_node)
      
    def clearViewingNode(self):
      self.animation_root_np_.clearCompass()
        
    def setSpriteAnimations(self,sprite_animator_dict):
        
        self.clearSpriteAnimations()
        
        for k,v in sprite_animator_dict:
            np = self.animation_root_np_.attachNewNode(v)
            np.hide()
            self.animators_[k] = np
            
        # selecting first animation
        keys = list(sprite_animator_dict.keys())
        self.pose(keys[0])
        
    def addSpriteAnimation(self,name,sprite_animator,
                           align = (AnimationSpriteAlignment.BOTTOM_CENTER_ALIGN),
                           center_offset = Vec3(0,0,0)):
        
        np = sprite_animator.instanceTo(self.animation_root_np_)
        np.hide()
        self.animators_[name] = np
        
        # setting the node's location
        pos = Vec3(0,0,0)
        bounds = np.getTightBounds()
        min = Vec3(bounds[0])
        max = Vec3(bounds[1])
        extends = max - min
                
        # Sprites origin is at the image's topleft corner
        if (align & AnimationSpriteAlignment.TOP_ALIGN) == AnimationSpriteAlignment.TOP_ALIGN:
            pos.setZ(self.size_.getZ())            
        elif (align & AnimationSpriteAlignment.BOTTOM_ALIGN) == AnimationSpriteAlignment.BOTTOM_ALIGN:
            pos.setZ(extends.getZ())
            
        if (align & AnimationSpriteAlignment.RIGHT_ALIGN) == AnimationSpriteAlignment.RIGHT_ALIGN:
            pos.setX(-0.5*self.size_.getX() - (self.size_.getX()- extends.getX())) 
        elif (align & AnimationSpriteAlignment.LEFT_ALIGN) == AnimationSpriteAlignment.LEFT_ALIGN:
            pos.setX(-0.5*self.size_.getX())                        
        elif (align & AnimationSpriteAlignment.CENTER_ALIGN_HORIZONTAL) == AnimationSpriteAlignment.CENTER_ALIGN_HORIZONTAL:
            logging.info("Centering horizontally")
            pos.setX(-0.5*extends.getX())
            
        if align == AnimationSpriteAlignment.CENTER_OFFSET_ALIGN:
            pos = center_offset
        
        np.setPos(self.animation_root_np_,pos)           
        
            
    def setAnimationEndCallback(self,cb):
        """
        Invokes the callback 'cb()' at the end of the animation. Pass 'None' to remove callback.
        """
        self.animation_end_cb_ = cb
    
    def setAnimationStartCallback(self,cb):  
        """
        Invokes the callback 'cb()' at the start of the animation. Pass 'None' to remove callback.
        """
        self.animation_start_cb_ = cb 
        
    def clearAllAnimationCallbacks(self):
      self.setAnimationEndCallback(None)
      self.setAnimationStartCallback(None)                  
            
    def clearSpriteAnimations(self):
        
        for np in list(self.animators_.values()):
            np.detachNode()          
        
        self.animators_ = {}
        
    def getCurrentAnimation(self):
        return self.selected_animation_name_
        
    def pose(self,animation_name, frame = 0):
        
        if animation_name not in self.animators_:
            logging.error( "Invalid animation name '%s'"%(animation_name))
            return False
        
        if self.selected_animation_name_ == animation_name:
            logging.warning(" Animation %s already selected"%(animation_name))
            return True
        
        # deselecting current node
        face_right = True
        if self.animator_np_ != None :
            
            face_right = self.animator_.isFacingRight()
            self.animator_.stop()
            self.animator_np_.hide()
            
        self.animator_np_ = self.animators_[animation_name]   
        self.animator_ = self.animator_np_.node().getPythonTag(SpriteAnimator.__name__)     
        self.animator_.faceRight(face_right)
        self.animator_.pose(frame)
        self.animator_np_.show()   
        self.selected_animation_name_ = animation_name    
        
        return True 
    
    def getNumFrames(self,animation_name =None):
        
        if animation_name == None :
            return self.animator_.getNumFrames()
        
        if animation_name in self.animators_:
            animator_np = self.animators_[animation_name]   
            animator = animator_np.node().getPythonTag(SpriteAnimator.PANDA_TAG)  
            return animator.getNumFrames()
        
        return -1
    
    def getFrame(self):
        if self.animator_np_ != None:
            return self.animator_.getFrame()
        else:
            return -1
            
    def getFrameRate(self,animation_name = None):
        if animation_name == None:
            return  self.animator_.getFrameRate()
        
        if animation_name in self.animators_:
            animator_np = self.animators_[animation_name]   
            animator = animator_np.node().getPythonTag(SpriteAnimator.PANDA_TAG)  
            return animator.getFrameRate()
            
    
    def selectFrame(self,frame):
      """
      Selects the frame of the current animation
      """  
      self.animator_.pose(frame) 
        
    def animate(self,animation_name):
      '''
      Animates the object in either play or loop mode depending on the current animation properties.
      '''    
      if self.pose(animation_name):            
        self.stop()            
        self.animator_.animate()
        self.__startFrameMonitor__()   
        
        
    def play(self,animation_name):
      '''
      Plays the animation once from beggining to end
      '''
        
      if self.pose(animation_name):            
          self.stop()            
          self.animator_.play()
          self.__startFrameMonitor__()
            
    def loop(self,animation_name):        
        
        if self.pose(animation_name):      
            self.stop()
            self.animator_.loop()
            self.__startFrameMonitor__()
            
    def stop(self):
        if self.animator_np_ != None:
            self.__stopFrameMonitor__()
            self.animator_.stop()
            
    def faceRight(self,face_right = True):
        if self.animator_np_ != None :
            self.animator_.faceRight(face_right)
            
    def isFacingRight(self):
        if self.animator_np_ is not None :
            return self.animator_.isFacingRight()
        
        
    ####################  Animation Frame Callback Triggering  #####################
        
    def __startFrameMonitor__(self):       
        
        # no callbacks then exit
        if (self.animation_start_cb_ is None) and (self.animation_end_cb_ is None):
            return
        
        # resetting sequence
        self.frame_monitor_seq_ = Sequence() 
        
        # invoking start callback
        if self.animation_start_cb_ is not None:
            self.animation_start_cb_()
        
        # monitor animation end in PLAYING 
        if self.animator_.getAnimationStatus() == SpriteAnimator.AnimationStatus.PLAYING : 
          finterv = Func(lambda n = (self.getNumFrames()-1) : self.__monitorEndInAnimationStatus__(n))
          self.frame_monitor_seq_.append(finterv)
        
        # monitoranimation end in LOOPING    
        if self.animator_.getAnimationStatus() == SpriteAnimator.AnimationStatus.LOOPING :
          self.triggered_callbacks_ = True
          finterv = Func(self.__monitorInLoopMode__)
          self.frame_monitor_seq_.append(finterv)
            
        self.frame_monitor_seq_.loop()
        
    def __stopFrameMonitor__(self):
      
        if self.frame_monitor_seq_ is not None:        
          self.frame_monitor_seq_.finish()  
          self.frame_monitor_seq_ = None     
        
            
    def __monitorEndInAnimationStatus__(self,last_frame):
        
        if (not self.animator_.isPlaying()) and (self.getFrame() == last_frame):
            
            self.animation_end_cb_()
            self.__stopFrameMonitor__() 
            
            
    def __monitorInLoopMode__(self):
        
        ##logging.debug("Looping animation " + self.selected_animation_name_)            
        if self.getFrame() == 0:
            
            if self.triggered_callbacks_:
                return
            
            # invoke callbacks
            if self.animation_start_cb_ is not None:
                self.animation_start_cb_()
                
            if self.animation_end_cb_ is not None:
                self.animation_end_cb_()
                
            self.triggered_callbacks_ = True
        else:
            self.triggered_callbacks_ = False
            
            
            
        
        
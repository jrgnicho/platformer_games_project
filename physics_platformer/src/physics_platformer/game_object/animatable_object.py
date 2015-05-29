from physics_platformer.game_object import GameObject
from physics_platformer.sprite import SpriteAnimator
from panda3d.core import BitMask16
from panda3d.core import Vec3
from panda3d.core import TransparencyAttrib


class AnimationSpriteAlignment(object):
    
    TOP_ALIGN = BitMask16.bit(0)
    BOTTOM_ALIGN = BitMask16.bit(1)
    LEFT_ALIGN = BitMask16.bit(2)
    RIGHT_ALIGN = BitMask16.bit(3)
    TOP_RIGHT_ALIGN = TOP_ALIGN | RIGHT_ALIGN
    TOP_LEFT_ALIGN = TOP_ALIGN | LEFT_ALIGN
    BOTTOM_RIGHT_ALIGN = BOTTOM_ALIGN | RIGHT_ALIGN
    BOTTOM_LEFT_ALIGN = BOTTOM_ALIGN | LEFT_ALIGN
    CENTER_ALIGN = BitMask16.bit(4)    
    CENTER_OFFSET_ALIGN = BitMask16.bit(5)
    

class AnimatableObject(GameObject):
    
    def __init__(self,name,size,mass,sprite_animator_dict = None):
        GameObject.__init__(self,name,size,mass,False) #creatin GameObject with a default box shape and no Visual
        self.setTransparency(TransparencyAttrib.M_alpha)
        self.node().setAngularFactor((0,0,0))  # no rotation
        self.animation_np_ = self.attachNewNode('sprite-animations')
        self.sprite_animators_ = {}
        self.selected_animation_name_ = ''
        self.animator_np_ = None # selected animator NodePath
        self.animator_ = None
        
        # callbacks
        self.animation_end_cb_ = None
        self.animation_start_cb_ = None
        
        if sprite_animator_dict != None:
            self.loadSpriteAnimations(sprite_animator_dict)
        
    def setSpriteAnimations(self,sprite_animator_dict):
        
        self.clearSpriteAnimations()
        
        for k,v in sprite_animator_dict:
            np = self.animation_np_.attachNewNode(v)
            np.hide()
            self.sprite_animators_[k] = np
            
        # selecting first animation
        keys = sprite_animator_dict.keys()
        self.pose(keys[0])
        
    def addSpriteAnimation(self,name,sprite_animator,align = AnimationSpriteAlignment.BOTTOM_ALIGN, center_offset = Vec3(0,0,0)):
        
        np = self.animation_np_.attachNewNode(sprite_animator)
        np.hide()
        self.sprite_animators_[name] = np
        
        # setting the node's location
        pos = Vec3(0,0,0)
        bounds = np.getTightBounds()
        min = Vec3(bounds[0])
        max = Vec3(bounds[1])
        extends = max - min
        
        
        if (align & AnimationSpriteAlignment.TOP_ALIGN) == AnimationSpriteAlignment.TOP_ALIGN:
            pos.setZ(0.5*self.size_.getZ() - 0.5*extends.getZ())            
        elif (align & AnimationSpriteAlignment.BOTTOM_ALIGN) == AnimationSpriteAlignment.BOTTOM_ALIGN:
            pos.setZ(-(0.5*self.size_.getZ() - 0.5*extends.getZ()))
            
        if (align & AnimationSpriteAlignment.RIGHT_ALIGN) == AnimationSpriteAlignment.RIGHT_ALIGN:
            pos.setX(0.5*self.size_.getX()- 0.5*extends.getX()) 
        elif (align & AnimationSpriteAlignment.LEFT_ALIGN) == AnimationSpriteAlignment.LEFT_ALIGN:
            pose.setX(-(0.5*self.size_.getX() - 0.5*extends.getX()))
            
        if align == AnimationSpriteAlignment.CENTER_OFFSET_ALIGN:
            pos = center_offset
        
        np.setPos(self,pos)     
        
        # selecting pose if none is
        if self.animator_np_ == None:
            self.pose(name)
            print "Selecting animation %s"%name
            
            
    def clearSpriteAnimations(self):
        
        for np in self.sprite_animators_.values():
            np.detachNode()          
        
        self.sprite_animators_ = {}
        
    def pose(self,animation_name, frame = 0):
        
        if not self.sprite_animators_.has_key(animation_name):
            print "ERROR: Invalid animation name '%s'"%(animation_name)
            return False
        
        if self.selected_animation_name_ == animation_name:
            print "WARNING: Animation %s already selected"%(animation_name)
            return True
        
        # deselecting current node
        face_right = True
        if self.animator_np_ != None :
            
            face_right = self.animator_.isFacingRight()
            self.animator_.stop()
            self.animator_np_.hide()
            
        self.animator_np_ = self.sprite_animators_[animation_name]   
        self.animator_ = self.animator_np_.node().getPythonTag(SpriteAnimator.PANDA_TAG)     
        self.animator_.faceRight(face_right)
        self.animator_.pose(frame)
        self.animator_np_.show()       
        
        return True 
    
    def getNumFrames(self,animation_name =None):
        
        if animation_name == None :
            return self.animator_.getNumFrames()
        
        if self.sprite_animators_.has_key(animation_name):
            animator_np = self.sprite_animators_[animation_name]   
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
        
        if self.sprite_animators_.has_key(animation_name):
            animator_np = self.sprite_animators_[animation_name]   
            animator = animator_np.node().getPythonTag(SpriteAnimator.PANDA_TAG)  
            return animator.getFrameRate()
            
    
    def selectFrame(self,frame):
        """
        Selects the frame of the current animation
        """  
        self.animator_.pose(frame)        
        
        
    def play(self,animation_name):
        
        if self.pose(animation_name):
            self.animator_.play()
            
    def loop(self,animation_name):
        
        if self.pose(animation_name):
            self.animator_.loop()
            
    def stop(self):
        if self.animator_np_ != None:
            self.animator_.stop()
            
    def faceRight(self,face_right = True):
        if self.animator_np_ != None :
            self.animator_.faceRight(face_right)
            
    def isFacingRight(self):
        if self.animator_np_ is not None :
            return self.animator_.isFacingRight()
        
    def __monitorFrames__(self):
        
        observed_frames ={} # dictionary of (int frame, Bool notify)
        if self.animation_start_cb_ is not None:
            observed_frames[0] = True
        if self.animation_end_cb_ is not None:
            observed_frames[self.getNumFrames() - 1] = True
            
        
        
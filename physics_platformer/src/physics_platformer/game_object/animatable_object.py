from physics_platformer.game_object import GameObject
from physics_platformer.sprite import SpriteAnimator
from panda3d.core import BitMask16
from panda3d.core import Vec3
from _ast import alias


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
    
    def __init__(self,name,size,mass,sprite_animator_dict):
        GameObject.__init__(name,size,mass,False) #creatin GameObject with a default box shape and no Visual
        self.node().setAngularFactor(0,0,0)  # no rotation
        self.animation_np_ = self.attachNewNode('sprite-animations')
        self.sprite_animators_ = {}
        self.selected_animation_name_ = ''
        self.selected_animator_ = None
        
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
        
        
        if (align & AnimationSpriteAlignment.TOP_ALIGN) == AnimationSpriteAlignment.TOP_ALIGN:
            pos.setZ(0.5*self.size_.getZ() - max.getZ())            
        elif (align & AnimationSpriteAlignment.BOTTOM_ALIGN) == AnimationSpriteAlignment.BOTTOM_ALIGN:
            pos.setZ(-0.5*self.size_.getZ() - min.getZ())
            
        if (align & AnimationSpriteAlignment.RIGHT_ALIGN) == AnimationSpriteAlignment.RIGHT_ALIGN:
            pos.setX(0.5*self.size_.getX()- max.getX()) 
        elif (align & AnimationSpriteAlignment.LEFT_ALIGN) == AnimationSpriteAlignment.LEFT_ALIGN:
            pose.setX(-0.5*self.size_.getX() - min.getX())
            
        if align == AnimationSpriteAlignment.CENTER_OFFSET_ALIGN:
            pos = center_offset
            
        np.setPos(pos)     
        
        # selecting pose if none is
        if self.selected_animator_ == None:
            self.pose(name)
            
            
    def clearSpriteAnimations(self):
        
        for np in self.sprite_animators_.values():
            np.detachNode()          
        
        self.sprite_animators_ = {}
        
    def pose(self,animation_name, frame = 0):
        
        if not self.sprite_animators_.has_key(animation_name):
            print "ERROR: Invalid animation name '%s'"%(animation_name)
            return False
        
        if self.selected_animation_name_ == animation_name:
            return True
        
        # deselecting current node
        face_right = True
        if self.selected_animator_ != None :
            
            faceRight = self.selected_animator_.node().isFacingRight()
            self.selected_animator_.node().stop()
            self.selected_animator_.hide()
            
        self.selected_animator_ = self.sprite_animators_[animation_name]        
        self.selected_animator_.node().faceRight(face_right)
        self.selected_animator_.node().pose(frame)
        self.selected_animator_.show()       
        
        return True 
    
    def getNumFrames(self,animation_name =None):
        
        if animation_name == None :
            return self.selected_animator_.node().getNumFrames()
        
        if self.sprite_animators_.has_key(animation_name):
            return (self.sprite_animators_[animation_name]).node().getNumFrames()
        
        return -1
            
    
    def selectFrame(self,frame):
        """
        Selects the frame of the current animation
        """  
        self.selected_animator_.node().pose(frame)        
        
        
    def play(self,animation_name):
        
        if self.pose(animation_name):
            self.selected_animator_.node().play()
            
    def loop(self,animation_name):
        
        if self.pose(animation_name):
            self.selected_animator_.node().loop()
            
    def stop(self):
        if self.selected_animator_ != None:
            self.selected_animator_.node().stop()
            
    def faceRight(self,face_right = True):
        if self.selected_animator_ != None :
            self.selected_animator_.node().faceRight(face_right)
            
    def isFacingRight(self):
        if self.selected_animator_ != None :
            self.selected_animator_.node().isFacingRight()
            
        
        
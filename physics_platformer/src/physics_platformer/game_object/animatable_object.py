from physics_platformer.game_object import GameObject
from physics_platformer.sprite import SpriteAnimator
from OpenGL.raw._GLX import Visual

class AnimatableObject(GameObject):
    
    def __init__(self,name,size,mass,sprite_animator_dict):
        GameObject.__init__(name,size,mass,None,False) #creatin GameObject with a default box shape and no Visual
        self.animation_np_ = self.attachNewNode('sprite-animations')
        self.sprite_animators_ = {}
        self.selected_animation_name_ = ''
        self.selected_animator_ = None
        
    def loadSpriteAnimations(self,sprite_animator_dict):
        
        self.clearSpriteAnimations()
        
        for k,v in sprite_animator_dict:
            np = self.animation_np_.instanceTo(v)
            np.hide()
            self.sprite_animators_[k] = np
            
            
    def clearSpriteAnimations(self):
        
        for np in self.sprite_animators_.values():
            np.detachNode()          
        
        self.sprite_animators_ = {}
        
    def pose(self,animation_name):
        
        if not self.sprite_animators_.has_key(animation_name):
            print "ERROR: Invalid animation name '%s'"%(animation_name)
            return False
        
        if self.selected_animation_name_ == animation_name:
            return True
        
        # deselecting current node
        if self.selected_animator_ != None :
            self.selected_animator_.getActiveSequenceNP().node().stop()
            self.selected_animator_.getActiveSequenceNP().hide()
            
        self.selected_animator_ = self.sprite_animators_[animation_name]
        self.selected_animator_.show() 
        
        return True           
        
        
    def play(self,animation_name):
        
        if self.pose(animation_name):
            self.selected_animator_.getSelectedNP().node().play()
            
    def loop(self,animation_name):
        
        if self.pose(animation_name):
            self.selected_animator_.getSelectedNP().node().loop()
            
    def stop(self):
        if self.selected_animator_ != None:
            self.selected_animator_.getSelectedNP().node().stop()
            
        
        
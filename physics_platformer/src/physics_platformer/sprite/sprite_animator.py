from panda3d.core import LColor
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import PNMImage, PNMImageHeader, Filename
from panda3d.core import SequenceNode
from panda3d.core import CardMaker
from panda3d.core import Texture
from panda3d.core import TextureStage
from panda3d.core import TransparencyAttrib


class SpriteAnimator(NodePath):
    
    def __init__(self,name):
        
        NodePath.__init__(self,name)
        self.setTransparency(TransparencyAttrib.M_alpha)
        self.seq_left_np_ = None
        self.seq_right_np_ = None
        self.facing_right_ = True
        self.name_ = name
        self.size_ = (0,0) # (horizontal_scale, vertical_scale
        
    def loadImages(self,images_right, images_left,width,height):
        
        pass
        
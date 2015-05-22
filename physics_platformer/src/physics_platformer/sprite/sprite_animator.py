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
        self.size_ = (0,0) # (horizontal_scale, vertical_scale
    
    
    def loadImages(self,images_right, images_left,frame_rate, width = 1,height = 1):   
        """
        loadImages
            Loads the images for the right and left side of the sprite animation
            Inputs:
             - images_right: List containing PNMImage objects for tanimating the character when it is facing right.
             - images_left:  List containing PNMImage objects for animating the character when it is facing left.
             - frame_rate: Rate in hz at which the images will be played.
             - width: Size in the X dimension of the rectangle on which the image is drawn.
             - height: Size in the Z dimension of the rectangle on which the image is drawn.
        """
        
        if (len(images_right) == 0) or (len(images_left) == 0):
            print "ERROR: Found empty image list"
            return False
    
        # storing individual sprite size
        w = images_right[0].getXSize() # assumes that all images in the in 'images' array are the same size
        h = images_right[0].getYSize()
        self.size_ = (w,h) # image size in pixels
    
        self.seq_right_ = self.attachNewNode(self.createSequenceNode(self.getName() + '-right-seq',images_right,width,height,frame_rate))
        self.seq_left_ = self.attachNewNode(self.createSequenceNode(self.getName()+ '-left-seq',images_left,width,height,frame_rate))
        self.seq_right_.hide()
        self.seq_left_.hide()
    
        self.faceRight(True)      
    
        return True
    
    def createSequenceNode(self,name,images,w,h,scale_x,scale_y,frame_rate):
    
        seq = SequenceNode(name)
        w = images[0].getXSize() # assumes that all images in the in 'images' array are the same size
        h = images[0].getYSize()        
        
        for i in range(0,len(images)):
            
            img = images[i]
            #sprite_img = PNMImage(w,h)
            #sprite_img.addAlpha()
            #sprite_img.alphaFill(0)
            #sprite_img.fill(1,1,1)
            #sprite_img.copySubImage(img ,0 ,0 ,0 ,0,w ,h)
            
            # Load the image onto the texture
            texture = Texture()        
            texture.setXSize(w)
            texture.setYSize(h)
            texture.setZSize(1)    
            texture.load(img)
            texture.setWrapU(Texture.WM_border_color) # gets rid of odd black edges around image
            texture.setWrapV(Texture.WM_border_color)
            texture.setBorderColor(LColor(0,0,0,0))
            
            # creating CardMaker to hold the texture
            cm = CardMaker(name +    str(i))
            cm.setFrame(-0.5*scale_x,0.5*scale_x,-0.5*scale_y,0.5*scale_y)
            card = NodePath(cm.generate())            
            card.setTexture(texture)
            seq.addChild(card.node(),i)
         
        seq.setFrameRate(frame_rate)   
        print "Sequence Node %s contains %i frames of size %s"%(name,seq.getNumFrames(),str((w,h)))        
        return seq 
    
    def isFacingRight(self):
        return self.facing_right_
    
    def faceRight(self,face_right):

        if face_right: 
            self.seq_left_.node().stop()
            self.seq_left_.hide()
            self.seq_right_.show()    
    
        else:
            self.seq_right_.node().stop()
            self.seq_right_.hide()
            self.seq_left_.show()    
    
        self.facing_right_ = face_right    
        
    def getSelectedNP(self):
        """
        Returns the active NodePath containing the active SequenceNode (either left or right)
        """
        return self.seq_right_ if self.facing_right_ else self.seq_left_
            
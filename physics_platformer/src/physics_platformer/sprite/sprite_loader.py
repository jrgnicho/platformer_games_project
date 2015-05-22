
from panda3d.core import LColor
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import PNMImage, PNMImageHeader, Filename
from panda3d.core import SequenceNode
from panda3d.core import CardMaker
from panda3d.core import Texture
from panda3d.core import TextureStage
from panda3d.core import TransparencyAttrib

class SpriteSequenceLoader:
    
    def __init__(self):
        pass
    
    def loadSpriteImages(self,file_path,cols,rows,flipx = False,flipy = False):
        """
        Loads an image file containing individual animation frames and returns then in a list of PNMImages
        inputs:
            - file_path
            - cols
            - rows
            - flipx
            - flipy
        Output: 
            - tuple ( bool , list[PNMImage]  )
        """
        
        # Make a filepath
        image_file = Filename(file_path)
        if image_file .empty():
            raise IOError, "File not found"
            return (False, [])
    
        # Instead of loading it outright, check with the PNMImageHeader if we can open
        # the file.
        img_head = PNMImageHeader()
        if not img_head.readHeader(image_file ):
            raise IOError, "PNMImageHeader could not read file %s. Try using absolute filepaths"%(file_path)
            return (False, [])
    
        # Load the image with a PNMImage
        full_image = PNMImage(img_head.getXSize(),img_head.getYSize())
        full_image.alphaFill(0)
        full_image.read(image_file) 
        
        if flipx or flipy:
            full_image.flip(flipx,flipy,False)
    
        w = int(full_image.getXSize()/cols)
        h = int(full_image.getYSize()/rows)
        
        images = []
    
        counter = 0
        for i in range(0,cols):
          for j in range(0,rows):
            sub_img = PNMImage(w,h)
            sub_img.addAlpha()
            sub_img.alphaFill(0)
            sub_img.fill(1,1,1)
            sub_img.copySubImage(full_image ,0 ,0 ,i*w ,j*h ,w ,h)
    
            images.append(sub_img)
            
        return (True, images)
        
    def flipImages(self,images,flipx , flipy):
        """
        Returns a copy of the images flipped by the corresponding axes
        """
        
        flipped = []
        for img in images: 
            fimg = PNMImage(img.getXSize(),img.getYSize())  
            fimg.copyFrom(img)        
            fimg.flip(flipx,flipy,False)
            flipped.append(fimg)
            
        return flipped
            
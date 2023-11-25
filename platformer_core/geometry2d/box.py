from shapely.geometry import box
import logging


class Box2D(object):
  
  def __init__(self,w,h,center,scale = (1,1)):
    """
    Box2D(double w,double h,(double, double) center, (double, double) scale = (1,1))
    Creates a 2D box for performing collision checks 
    Inputs:
    - w: width. horizontal extent
    - h: Height, vertical extent
    - center: x, y location of the box's center. x+ point towards the right while y+ points up 
    - scale : x, y values that scale the box's dimensions.
    """
    
    self.top_ = 0
    self.bottom_ = 0
    self.left_ = 0
    self.right_ = 0
    self.w_ = w
    self.h_ = h
    self.centerx_ = center[0]
    self.centery_ = center[1]   
    self.scalex_ = scale[0]
    self.scaley_ = scale[1]
    self.__update__()
    
  @property
  def top(self):
    return self.top_
  
  @property
  def bottom(self):
    return self.bottom_
  
  @property
  def left(self):
    return self.left_
  
  @property
  def right(self):
    return self.right_
  
  @property 
  def center(self):
    
    return (self.centerx_* self.scalex_,self.centery_* self.scaley_)
  
  @center.setter
  def center(self,c):
    
    self.centerx_ = c[0]
    self.centery_ = c[1]    
    self.__update__()
  
  @property
  def size(self):
    return (self.w_ * self.scalex_ ,self.h_ *self.scaley_)
  
  @size.setter
  def size(self,s):
    self.w_ = s[0]
    self.h_ = s[1]
    self.__update__()
    
  @property
  def width(self):
    return self.w_ * self.scalex_
  
  @property
  def height(self):
    return self.h_ *self.scaley_
    
  @property
  def scale(self):
    return (self.scalex_,self.scaley_)
  
  @scale.setter
  def scale(self,sc):
    """
    scale((double, double) sc)    
    """
    
    self.scalex_ = sc[0]
    self.scaley_ = sc[1]    
    self.__update__()
    
  def __str__(self):
    s = 'left: %f, top: %f, right: %f, bottom: %f'%(self.left_,self.top_,self.right_,self.bottom_)
    return s
  
  def flipX(self,xoffset = 0):
    v = self.centerx_ - xoffset    
    new_centerx = xoffset - v    
    return Box2D(self.w_,self.h_,(new_centerx,self.centery_),(self.scalex_,self.scaley_))
    
  def checkCollision(self,box2d,c1 = (0,0), c2 = (0,0)):
    """
    Checks if this box overlaps with the input box at the designated box center locations c1 and c2.  Returns True | False
    """
    
    b1 = self.__getCollisionBox__(c1)
    b2 = box2d.__getCollisionBox__(c2)
    return b1.intersects(b2)
  
  @staticmethod
  def createBoundingBox(boxes):
    """
    Box2D.createBoundingBox([Box2D] boxes) -> Box2D
    Creates a bounding box that contains all the boxes in the list
    """
    
    if len(boxes) == 0:
      logging.error("Passed an empty Box2D list")
      return None    
   
    if type(boxes[0]) is not Box2D:
      logging.error("Elements in list arent of the Box2D type")
      return None
    
    b_union = boxes[0].__getCollisionBox__((0,0))
    for b in boxes[1:]:
      b_union = b_union.union(b.__getCollisionBox__((0,0)))
    
    w = b_union.bounds[2] - b_union.bounds[0]
    h = b_union.bounds[3] - b_union.bounds[1]
    cx = b_union.bounds[0] + 0.5*w
    cy = b_union.bounds[1] + 0.5*h
    
    return Box2D(w,h,(cx,cy))
    
  def __update__(self):
    
    self.top_ = (0.5*self.h_ + self.centery_) * self.scaley_
    self.bottom_ = (-0.5*self.h_ + self.centery_) * self.scaley_
    self.left_ = (-0.5*self.w_ + self.centerx_) * self.scalex_
    self.right_ = (0.5*self.w_ + self.centerx_) * self.scalex_
    
  def __getCollisionBox__(self,center):
    return box(self.left_ + center[0],
               self.bottom_ + center[1],
               self.right_ + center[0],
               self.top_ + center[1])
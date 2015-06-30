from shapely.geometry import box


class Box2D(object):
  
  def __init__(self,w,h,center):
    """
    Box2D(double w,double h,(double, double) center)
    Creates a 2D box for performing collision checks 
    Inputs:
    - w: width. horizontal extent
    - h: Height, vertical extent
    - center: x, y location of the box's center. x+ point towards the right while y+ points up 
    """
    
    self.top_ = 0
    self.bottom_ = 0
    self.left_ = 0
    self.right_ = 0
    self.w_ = w
    self.h_ = h
    self.centerx_ = center[0]
    self.centery_ = center[1]    
    self.__update__()
  
  @property 
  def center(self):
    
    return (self.centerx_,self.centery_)
  
  @center.setter
  def center(self,c):
    
    self.centerx_ = c[0]
    self.centery_ = c[1]    
    self.__update__()
  
  @property
  def size(self):
    return (self.w_,self.h_)
  
  @size.setter
  def size(self,s):
    self.w_ = s[0]
    self.h_ = s[1]
    
  def checkCollision(self,box2d):
    """
    Checks if this box overlaps with the input box.  Returns True | False
    """
    
    b1 = self.__getCollisionBox__()
    b2 = box2d.__getCollisionBox__()
    return b1.intersects(b2)
    
  def __update__(self):
    
    self.top_ = 0.5*self.h_ + self.centery_
    self.bottom_ = -0.5*self.h + self.centery_
    self.left_ = -0.5*self.w + self.centerx_
    self.right_ = 0.5*self.w + self.centerx_
    
  def __getCollisionBox__(self):
    return box(self.left_,self.bottom_,self.right_,self.top_)
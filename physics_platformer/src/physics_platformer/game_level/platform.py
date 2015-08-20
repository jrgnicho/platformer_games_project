
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletGhostNode
from physics_platformer.game_object import GameObject

class Platform(GameObject):
  
  __PERIMETER_BOX_SIDE__ = 0.01
  def __init__(self,name,size):
    GameObject.__init__(self,name,size,0)
    
    # creating Bullet Ghost boxes around the perimeter 
    width = size.getX()
    height = size.getZ()
    thickness = size.getY()
    left_box = BulletGhostNode(name + 'perimeter-left')
    
    
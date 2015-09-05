from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletGhostNode
from physics_platformer.game_object import GameObject
from physics_platformer.collision_masks import *
from physics_platformer.src.physics_platformer.collision_masks.collision_masks import CollisionMasks

class Platform(GameObject):
  
  __PERIMETER_THICKNESS__ = 0.01
  __LEDGE_BOX_SIDE_LENGHT = 0.01
  def __init__(self,name,size):
    GameObject.__init__(self,name,size,0)
    self.setIntoCollideMask(CollisionMasks.LEVEL_OBSTACLE)
    
    # creating Bullet Ghost boxes around the perimeter 
    width = size.getX()
    height = size.getZ()
    depth = size.getY()
    
    # half dimensions
    half_width = 0.5*width
    half_height = 0.5*height
    half_depth = 0.5*depth
    half_thickness = 0.5*Platform.__PERIMETER_THICKNESS__
    ghost_nodes = []
    
    left_box = BulletGhostNode(name + 'surface-left')    
    left_box.addShape(BulletBoxShape(Vec3(half_thickness,half_depth,half_height),
                                     TransformState.makePos(-half_width+half_thickness,0,0)))
    left_box.setIntoCollideMask(CollisionMasks.LEFT_WALL_SURFACE)
    ghost_nodes.append(left_box)
    
    right_box = BulletGhostNode(name + 'surface-right')    
    right_box.addShape(BulletBoxShape(Vec3(half_thickness,half_depth,half_height),
                                     TransformState.makePos(half_width-half_thickness,0,0)))    
    right_box.setIntoCollideMask(CollisionMasks.RIGHT_WALL_SURFACE)
    ghost_nodes.append(right_box)
    
    top_box = BulletGhostNode(name + 'surface-top')    
    top_box.addShape(BulletBoxShape(Vec3(half_width,half_depth,half_thickness),
                                     TransformState.makePos(0,0,half_height- half_thickness)))
    top_box.setIntoCollideMask(CollisionMasks.LANDING_SURFACE)
    ghost_nodes.append(top_box)
    
    bottom_box = BulletGhostNode(name + 'surface-bottom')    
    bottom_box.addShape(BulletBoxShape(Vec3(half_width,half_depth,half_thickness),
                                     TransformState.makePos(0,0,-half_height + half_thickness)))
    bottom_box.setIntoCollideMask(CollisionMasks.CEILING_SURFACE)
    ghost_nodes.append(bottom_box)
    
    # creating ledges
    half_side_lenght = 0.5*Platform.__LEDGE_BOX_SIDE_LENGHT
    
    left_ledge = BulletGhostNode('ledge-left')
    left_ledge.addShape(BulletBoxShape(Vec3(half_side_lenght,half_depth,half_side_lenght)),
                        TransformState.makePos(Vec3(-half_width + half_side_lenght,0,half_height)))
    left_ledge.setIntoCollideMask(CollisionMasks.LEDGE)
    ghost_nodes.append(left_ledge)
    
    right_ledge = BulletGhostNode('ledge-right')
    right_ledge.addShape(BulletBoxShape(Vec3(half_side_lenght,half_depth,half_side_lenght)),
                        TransformState.makePos(Vec3(half_width - half_side_lenght,0,half_height)))
    right_ledge.setIntoCollideMask(CollisionMasks.LEDGE)
    ghost_nodes.append(right_ledge)
    
    # adding all ghost nodes
    for gn in ghost_nodes:
      self.attachNewNode(gn)
    
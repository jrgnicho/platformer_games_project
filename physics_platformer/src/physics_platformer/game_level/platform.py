from panda3d.core import Vec3
from panda3d.core import TexturePool
from panda3d.core import TransformState
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletGhostNode
from physics_platformer.game_object import GameObject
from physics_platformer.collision import *

class Platform(GameObject):
  
  __PERIMETER_THICKNESS__ = 0.25
  __LEDGE_BOX_SIDE_LENGHT = 0.01
  __DEFAULT_TEXTURE__ = TexturePool.loadTexture(GameObject.DEFAULT_RESOURCES_DIRECTORY +'/models/iron.jpg')
  def __init__(self,name,size):
    GameObject.__init__(self,name,size,0)
    self.setCollideMask(CollisionMasks.LEVEL_OBSTACLE)
    self.visual_nh_.setTexture(Platform.__DEFAULT_TEXTURE__,1) 
    #self.visual_nh_.hide()
    #self.hide()
    
    # creating Bullet Ghost boxes around the perimeter 
    width = size.getX()
    height = size.getZ()
    depth = size.getY()
    
    # half dimensions
    half_width = 0.5*width
    half_height = 0.5*height
    half_depth = 0.5*depth
    half_thickness = 0.5*Platform.__PERIMETER_THICKNESS__
    padding = half_thickness
    self.ghost_nodes_ = []
    
    left_box = BulletGhostNode(name + 'surface-left')    
    left_box.addShape(BulletBoxShape(Vec3(half_thickness,half_depth,half_height)),
                                     TransformState.makePos(Vec3(-half_width+padding,0,0)))
    left_box.setIntoCollideMask(CollisionMasks.LEFT_WALL_SURFACE)
    self.ghost_nodes_.append(left_box)
    
    right_box = BulletGhostNode(name + 'surface-right')    
    right_box.addShape(BulletBoxShape(Vec3(half_thickness,half_depth,half_height)),
                                     TransformState.makePos(Vec3(half_width-padding,0,0) ) )                            
    right_box.setIntoCollideMask(CollisionMasks.RIGHT_WALL_SURFACE)
    self.ghost_nodes_.append(right_box)
    
    top_box = BulletGhostNode(name + 'surface-top')    
    top_box.addShape(BulletBoxShape(Vec3(half_width,half_depth,half_thickness)),
                                     TransformState.makePos(Vec3(0,0,half_height- padding) ) )
    top_box.setIntoCollideMask(CollisionMasks.LANDING_SURFACE)
    self.ghost_nodes_.append(top_box)
    
    bottom_box = BulletGhostNode(name + 'surface-bottom')    
    bottom_box.addShape(BulletBoxShape(Vec3(half_width,half_depth,half_thickness)),
                                     TransformState.makePos(Vec3(0,0,-half_height + padding)))
    bottom_box.setIntoCollideMask(CollisionMasks.CEILING_SURFACE)
    self.ghost_nodes_.append(bottom_box)
    
    # creating ledges
    half_side_lenght = 0.5*Platform.__LEDGE_BOX_SIDE_LENGHT
    
    left_ledge = BulletGhostNode('ledge-left')
    left_ledge.addShape(BulletBoxShape(Vec3(half_side_lenght,half_depth,half_side_lenght)),
                        TransformState.makePos(Vec3(-half_width + half_side_lenght,0,half_height)))
    left_ledge.setIntoCollideMask(CollisionMasks.LEDGE)
    self.ghost_nodes_.append(left_ledge)
    
    right_ledge = BulletGhostNode('ledge-right')
    right_ledge.addShape(BulletBoxShape(Vec3(half_side_lenght,half_depth,half_side_lenght)),
                        TransformState.makePos(Vec3(half_width - half_side_lenght,0,half_height)))
    right_ledge.setIntoCollideMask(CollisionMasks.LEDGE)
    self.ghost_nodes_.append(right_ledge)
    
    # adding all ghost nodes
    for gn in self.ghost_nodes_:
      self.attachNewNode(gn)
      
  def setObjectID(self,id):
    GameObject.setObjectID(self,id)
    for gh in self.ghost_nodes_:
      gh.setPythonTag(GameObject.ID_PYTHON_TAG,str(id))
      
  def setPhysicsWorld(self,physics_world): 
    GameObject.setPhysicsWorld(self,physics_world)
    
    for gn in self.ghost_nodes_:
      self.physics_world_.attach(gn)
      
  def clearPhysicsWorld(self):
    for gn in self.ghost_nodes_:
      self.physics_world_.remove(gn)
    GameObject.clearPhysicsWorld(self)
      
  def execute(self):
    pass
    
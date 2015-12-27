
from panda3d.core import Vec3
from panda3d.core import Mat4
from panda3d.core import TransformState
from panda3d.core import NodePath
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletWorld
from physics_platformer.game_level import Platform
from physics_platformer.collision import CollisionMasks
from physics_platformer.game_actions import CollisionAction
from physics_platformer.collision import CollisionActionMatrix
from physics_platformer.game_object import GameObject
import logging

class Level(NodePath):
  
  __BOUND_THICKNESS_ = 10.0
  __BOUND_DEPTH_ = 1.0 # y direction
  __GRAVITY__ = Vec3(0,0,-14)
  __PHYSICS_SIM_SUBSTEPS__ = 5
  __PHYSICS_SIM_STEPSIZE__ = 1.0/180.0
  
  def __init__(self,name,size):
    """
    Level(string name, Vec3 size)
    Creates a Level object.
    """
    
    NodePath.__init__(self,name)
    self.physics_world_ = BulletWorld()
    self.physics_world_.setGravity(Level.__GRAVITY__)
    self.size_ = size   
    self.bound_boxes_ = [] # node paths to rigid bodies 
    self.game_object_map_ = {}  # game objects in the world
    self.free_falling_objects_ = {}  # dynamic dictionary for notifying free falling
    self.id_counter_ = 0
    self.collision_action_matrix_ = CollisionActionMatrix()
    self.platforms_ = {}
    
    self.__createLevelBounds__()
    self.__createCollisionRules__()
    
  def detachNode(self):
    
    # removing game objects
    for gobj in self.game_object_map_.values():
      if self.platforms_.has_key(gobj.getObjectID()):
        continue
      
      gobj.clearPhysicsWorld()
      
    NodePath.detachNode(self)
    
  def getPhysicsWorld(self):
    return self.physics_world_
    
  def __del__(self):  
    
    self.detachNode()  

    # removing platforms
    for pltf in self.platforms_.values():
      pltf.clearPhysicsWorld()
    
    # removing all remaining objects from physics world
    objs = self.physics_world_.getRigidBodies() 
    num_objects = len(objs)
    for obj in objs:          
      self.physics_world_.remove(obj)
      logging.debug("Removed rigid body %s"%(obj.getName()))
      
    objs = self.physics_world_.getConstraints() 
    num_objects = len(objs)
    logging.debug("Removing %i constraints from level"%(num_objects))
    for obj in objs:     
      self.physics_world_.remove(obj)
    
    objs = self.physics_world_.getGhosts() 
    num_objects = len(objs)
    logging.debug("Removing %i ghosts bodies from level"%(num_objects))
    for obj in objs:     
      self.physics_world_.remove(obj)
    
    if not self.isSingleton(): 
      num_objects = self.getNumChildren()
      for i in range(0,num_objects):
        np = self.getChild(i)
        np.detachNode()
        
      
    self.game_object_map_ = {}
    self.platforms_ = {}
    
  def addPlatform(self,platform):    
    platform.setPhysicsWorld(self.physics_world_)
    platform.reparentTo(self)
    new_id = 'platform-'+str(len(self.platforms_))
    platform.setObjectID(new_id)
    self.platforms_[platform.getObjectID()] = platform
    self.game_object_map_[platform.getObjectID()] = platform
    
  def addGameObject(self,game_object):    
    self.id_counter_+=1
    new_id = 'game-object-' + str(self.id_counter_)
    game_object.setObjectID(new_id)    
    self.game_object_map_[game_object.getObjectID()] = game_object
    game_object.setPhysicsWorld(self.physics_world_)
    game_object.reparentTo(self)   
    self.free_falling_objects_[new_id] = True 
  
  def update(self,dt):
    self.physics_world_.doPhysics(dt, Level.__PHYSICS_SIM_SUBSTEPS__, Level.__PHYSICS_SIM_STEPSIZE__)
    
    for obj in self.game_object_map_.values():
      obj.update(dt)
    
    self.__processCollisions__()    
    
  def __createLevelBounds__(self): 
    
    bound_names = ['top', 'right', 'bottom','left'] # clockwise order
    
    half_thickness = 0.5*Level.__BOUND_THICKNESS_
    half_depth = 0.5*Level.__BOUND_DEPTH_
    half_sizes = [Vec3(0.5*self.size_.getX(), half_depth, half_thickness),
                  Vec3(half_thickness, half_depth, 0.5*self.size_.getZ()),
                  Vec3(0.5*self.size_.getX(), half_depth, half_thickness),
                  Vec3(half_thickness, half_depth, 0.5*self.size_.getZ())]
    
    poses = [TransformState.makePos(Vec3(0,0,0.5*self.size_.getZ())),
             TransformState.makePos(Vec3(0.5*self.size_.getX(),0,0)),
             TransformState.makePos(Vec3(0,0,-0.5*self.size_.getZ())),
             TransformState.makePos(Vec3(-0.5*self.size_.getX(),0,0))]
    
    for i in range(0,4):
      
      bound_box = BulletRigidBodyNode(self.getName() + '-' + bound_names[i] + '-bound')
      bound_box.addShape(BulletBoxShape(half_sizes[i]))
      bound_box.setMass(0)
      bound_box.setIntoCollideMask(CollisionMasks.LEVEL_BOUND)
      np = self.attachNewNode(bound_box)
      self.physics_world_.attach(bound_box)
      np.setTransform(poses[i])
      self.bound_boxes_.append(np)   
      
  def __createCollisionRules__(self):
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_TOP.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_LEFT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_RIGHT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_AABB.getLowestOnBit(),CollisionMasks.LEVEL_BOUND.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.GAME_OBJECT_AABB.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),True)    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.ACTION_BODY.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),True)
    
    # populating collision action matrix
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_BOTTOM.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.SURFACE_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_TOP.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.CEILING_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_LEFT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.LEFT_WALL_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_RIGHT.getLowestOnBit(),CollisionMasks.LEVEL_OBSTACLE.getLowestOnBit(),CollisionAction.RIGHT_WALL_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.ACTION_BODY.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),CollisionAction.ACTION_BODY_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.GAME_OBJECT_AABB.getLowestOnBit(),CollisionMasks.LEVEL_BOUND.getLowestOnBit(),CollisionAction.COLLIDE_LEVEL_BOUND)
  
    logging.debug(str(self.collision_action_matrix_))
    
  def __processCollisions__(self):
    
    # reset free falling dictionary
    self.free_falling_objects_ = dict.fromkeys(self.free_falling_objects_,True)
    
    # processing contacts
    contact_manifolds = self.physics_world_.getManifolds()
    for cm in contact_manifolds:
      
      node0 = cm.getNode0()
      node1 = cm.getNode1()
      col_mask1 = node0.getIntoCollideMask()
      col_mask2 = node1.getIntoCollideMask()
      
      key1 = node0.getPythonTag(GameObject.ID_PYTHON_TAG)
      key2 = node1.getPythonTag(GameObject.ID_PYTHON_TAG)
            
      obj1 = self.game_object_map_[key1] if (key1 is not None and self.game_object_map_.has_key(key1)) else None
      obj2 = self.game_object_map_[key2] if (key2 is not None and self.game_object_map_.has_key(key2)) else None      
      
      if (obj1 is not None) and self.collision_action_matrix_.hasEntry(
                                                                       col_mask1.getLowestOnBit() , 
                                                                       col_mask2.getLowestOnBit()):
        
        action_key = self.collision_action_matrix_.getAction(col_mask1.getLowestOnBit() , col_mask2.getLowestOnBit())
        action = CollisionAction(action_key,obj1,obj2,cm)            
        obj1.execute(action)
                
        # check for free falling
        if self.free_falling_objects_.has_key(key1) and col_mask1 == CollisionMasks.GAME_OBJECT_BOTTOM:
          self.free_falling_objects_[key1] = False
        
      if (obj2 is not None) and self.collision_action_matrix_.hasEntry(
                                                                       col_mask2.getLowestOnBit() ,
                                                                       col_mask1.getLowestOnBit()):
        
        action_key = self.collision_action_matrix_.getAction(col_mask2.getLowestOnBit() , col_mask1.getLowestOnBit())
        action = CollisionAction(action_key,obj2,obj1,cm)
        obj2.execute(action)
        
        # check for free falling
        if self.free_falling_objects_.has_key(key2) and col_mask2 == CollisionMasks.GAME_OBJECT_BOTTOM:
          self.free_falling_objects_[key2] = False
    
    
    # objects in free fall      
    for id,free_fall in self.free_falling_objects_.items():      
      if free_fall:
        obj = self.game_object_map_[id]
        action = CollisionAction(CollisionAction.FREE_FALL,obj,None,None)
        obj.execute(action)
        
      
      

      
    
  
  
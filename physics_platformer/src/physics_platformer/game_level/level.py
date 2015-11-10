
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
  
  __BOUND_THICKNESS_ = 0.1
  __BOUND_DEPTH_ = 0.1 # y direction
  __GRAVITY__ = Vec3(0,0,-10)
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
    self.id_counter_ = 0
    self.collision_action_matrix_ = CollisionActionMatrix()
    self.platforms_ = []
    
    self.__createLevelBounds__()
    self.__createCollisionRules__()
    
  def detachNode(self):
    
    # removing game objects
    for gobj in self.game_object_map_.values():
      gobj.clearPhysicsWorld()
      
    NodePath.detachNode(self)
    
  def __del__(self):  
    
    self.detachNode()  

    # removing platforms
    for pltf in self.platforms_:
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
    self.platforms_ = []
    
  def addPlatform(self,platform):    
    platform.setPhysicsWorld(self.physics_world_)
    platform.reparentTo(self)
    self.platforms_.append(platform)
    
  def addGameObject(self,game_object):    
    self.id_counter_+=1
    new_id = self.id_counter_
    game_object.setObjectID(str(new_id))    
    self.game_object_map_[game_object.getObjectID()] = game_object
    game_object.setPhysicsWorld(self.physics_world_)
    game_object.reparentTo(self)    
  
  def update(self,dt):
    self.physics_world_.doPhysics(dt, Level.__PHYSICS_SIM_SUBSTEPS__, Level.__PHYSICS_SIM_STEPSIZE__)
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
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.RIGID_BODY.getLowestOnBit(),CollisionMasks.LANDING_SURFACE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.RIGID_BODY.getLowestOnBit(),CollisionMasks.CEILING_SURFACE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.RIGID_BODY.getLowestOnBit(),CollisionMasks.LEFT_WALL_SURFACE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.RIGID_BODY.getLowestOnBit(),CollisionMasks.RIGHT_WALL_SURFACE.getLowestOnBit(),True)
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.RIGID_BODY.getLowestOnBit(),CollisionMasks.LEVEL_BOUND.getLowestOnBit(),True)
    
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.ACTION_BODY.getLowestOnBit(),CollisionMasks.LEDGE.getLowestOnBit(),True)
    
    # populating collision action matrix
    self.collision_action_matrix_.addEntry(CollisionMasks.RIGID_BODY,CollisionMasks.LANDING_SURFACE,CollisionAction.SURFACE_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.RIGID_BODY,CollisionMasks.CEILING_SURFACE,CollisionAction.CEILING_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.RIGID_BODY,CollisionMasks.LEFT_WALL_SURFACE,CollisionAction.LEFT_WALL_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.RIGID_BODY,CollisionMasks.RIGHT_WALL_SURFACE,CollisionAction.RIGHT_WALL_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.ACTION_BODY,CollisionMasks.LEDGE,CollisionAction.ACTION_BODY_COLLISION)
    self.collision_action_matrix_.addEntry(CollisionMasks.RIGID_BODY,CollisionMasks.LEVEL_BOUND,CollisionAction.COLLIDE_LEVEL_BOUND)
  
  def __processCollisions__(self):
    
    n = self.physics_world_.getNumManifolds()
    for i in range(0,n):
      contact_manifold = self.physics_world_.getManifold(i)
      
      node0 = contact_manifold.getNode0()
      node1 = contact_manifold.getNode1()
      
      key1 = node0.getPythonTag(GameObject.ID_PYTHON_TAG)
      key2 = node1.getPythonTag(GameObject.ID_PYTHON_TAG)
      
      if (key1 is None) or (key2 is None) :
        return
      
      obj1 = self.game_object_map_[key1] if (key1 is not None) else None
      obj2 = self.game_object_map_[key2] if (key2 is not None) else None      
      
      if obj1 and self.collision_action_matrix_.hasEntry(node0.getIntoCollideMask() , node1.getIntoCollideMask()):
        action_key = self.collision_action_matrix_.getAction(node0.getIntoCollideMask() , node1.getIntoCollideMask())
        action = CollisionAction(action_key,obj1,obj2,contact_manifold)
                
        obj1.execute(action)
        logging.debug("Found collision action %s between '%s' and '%s'"%( action_key ,obj1.getName(),obj2.getName()))
        
      if obj2 and self.collision_action_matrix_.hasEntry(node1.getIntoCollideMask() , node0.getIntoCollideMask()):
        action_key = self.collision_action_matrix_.getAction(node1.getIntoCollideMask() , node0.getIntoCollideMask())
        action = CollisionAction(action_key,obj2,obj1,contact_manifold)
        
        obj2.execute(action)
        logging.debug("Found collision action %s between '%s' and '%s'"%( action_key ,obj2.getName(),obj1.getName()))
      
    
  
  
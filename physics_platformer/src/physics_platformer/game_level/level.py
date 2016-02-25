
from panda3d.core import Vec3
from panda3d.core import Mat4
from panda3d.core import TransformState
from panda3d.core import NodePath
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletWorld
from physics_platformer.collision import CollisionMasks
from physics_platformer.collision import CollisionActionMatrix
from physics_platformer.game_actions import CollisionAction
from physics_platformer.game_object import GameObject
from physics_platformer.game_level import Platform
from physics_platformer.game_level import LevelCollisionResolver
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
    self.game_object_map_ = {}  # game objects in the world including static and mobile
    self.mobile_object_ids_ = [] # list of object ids far all mobile objects
    self.id_counter_ = 0
    self.collision_action_matrix_ = CollisionActionMatrix()
    self.platforms_ = {}
    
    # collision handling
    self.collision_resolvers_ = []
    
    self.__createLevelBounds__()
    self.__setupCollisionRules__()
    
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
    
  def addCollisionResolver(self,resolver):
    """
    Adds a collision resolver which will be invoked on every update in order to resolve collisions between 
    the various objects in the level
    """
    resolver.setupCollisionRules(self.physics_world_)
    self.collision_resolvers_.append(resolver)
    
  def addPlatform(self,platform):    
    platform.setPhysicsWorld(self.physics_world_)
    platform.reparentTo(self)
    new_id = 'platform-'+str(len(self.platforms_))
    platform.setObjectID(new_id)
    self.game_object_map_[platform.getObjectID()] = platform
    
    # adding children of platform
    for obj in platform.getChildrenGameObjects():
      self.id_counter_+=1
      new_id = 'game-object-' + str(self.id_counter_)
      obj.setObjectID(new_id)
      self.game_object_map_[obj.getObjectID()] = obj
    
    
    self.platforms_[platform.getObjectID()] = platform
    
  def addGameObject(self,game_object):    
    self.id_counter_+=1
    new_id = 'game-object-' + str(self.id_counter_)
    game_object.setObjectID(new_id)    
    self.game_object_map_[game_object.getObjectID()] = game_object
    game_object.setPhysicsWorld(self.physics_world_)
    game_object.reparentTo(self)   
    self.mobile_object_ids_.append(new_id)
  
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
      
  def __setupCollisionRules__(self):
    
    resolver = LevelCollisionResolver()
    self.addCollisionResolver(resolver)      
    
  def __processCollisions__(self):
        
    # processing contacts
    contact_manifolds = self.physics_world_.getManifolds()
    
    unprocessed_contacts = []
    for r in self.collision_resolvers_:
      unprocessed_contacts = r.processCollisions(contact_manifolds,self.game_object_map_,self.mobile_object_ids_)
        
      
      

      
    
  
  
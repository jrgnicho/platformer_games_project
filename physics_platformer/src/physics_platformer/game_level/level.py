
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
from physics_platformer.game_level import Sector, SectorTransition
from physics_platformer.game_level import LevelCollisionResolver
import logging

class Level(NodePath):
  
  __BOUND_THICKNESS_ = 10.0
  __BOUND_DEPTH_ = 1.0 # y direction
  __GRAVITY__ = Vec3(0,0,-14)
  __PHYSICS_SIM_SUBSTEPS__ = 5
  __PHYSICS_SIM_STEPSIZE__ = 1.0/180.0
  
  def __init__(self,name,min_point, max_point):
    """
    Level(string name, Vec3 min_point, Vec3 max_point)
      Creates a Level object.
      
      @param name: The level name
      @param min_point: Level bounding box minimum point
      @param max_point: Level bounding box maximum point
    """
    
    NodePath.__init__(self,name)
    self.physics_world_ = BulletWorld()
    self.physics_world_.setGravity(Level.__GRAVITY__)
    
    # level bounds
    self.min_point_ = min_point
    self.max_point_ = max_point    
    self.size_ = max_point - min_point   
    self.bound_boxes_ = [] # node paths to rigid bodies 
    self.game_object_map_ = {}  # game objects in the world including static and mobile
    self.mobile_object_ids_ = [] # list of object ids far all mobile objects
    self.id_counter_ = 0
    self.collision_action_matrix_ = CollisionActionMatrix()
    self.platforms_ = {}
    
    # collision handling
    self.collision_resolvers_ = []
    
    # sectors
    self.sectors_dict_ = {}
    self.sectors_list_ = []
    self.active_sector_ = None
    
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
    
  def addSector(self,transform, name = ''):
    
    name = name if len(name) > 0 else self.getName() + '-sector-' + str(len(self.sectors_dict_))    
    sector = Sector(name,self,self.physics_world_,transform)
    self.sectors_dict_[sector.getName()] = sector
    self.sectors_list_.append(sector)
    return sector
    
  def getSectors(self):
    return self.sectors_list_
    
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
    
    logging.warn("The Level.__createLevelBounds__() method is currently disabled")
    return
    
    bound_names = ['top', 'right', 'bottom','left'] # clockwise order
    
    half_thickness = 0.5*Level.__BOUND_THICKNESS_
    half_depth = 0.5*Level.__BOUND_DEPTH_
    half_sizes = [Vec3(0.5*self.size_.getX(), half_depth, half_thickness),
                  Vec3(half_thickness, half_depth, 0.5*self.size_.getZ()),
                  Vec3(0.5*self.size_.getX(), half_depth, half_thickness),
                  Vec3(half_thickness, half_depth, 0.5*self.size_.getZ())]
    
    offset = self.min_point_ + self.size_*0.5
    poses = [TransformState.makePos(Vec3(0,0,0.5*self.size_.getZ()) + offset),
             TransformState.makePos(Vec3(0.5*self.size_.getX(),0,0) + offset),
             TransformState.makePos(Vec3(0,0,-0.5*self.size_.getZ()) + offset),
             TransformState.makePos(Vec3(-0.5*self.size_.getX(),0,0) + offset)]
    
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
    
    level_coll_resolver = LevelCollisionResolver()
    self.addCollisionResolver(level_coll_resolver)   
    
    # enabling sector detection
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.SECTOR_TRANSITION.getLowestOnBit(),CollisionMasks.GAME_OBJECT_ORIGIN.getLowestOnBit(),True)
    
  def __processSectorTransitions__(self,contact_manifolds):  
    processed_contacts = []
    
    num_contacts = len(contact_manifolds)
    for i in range(0,num_contacts):
      
      cm = contact_manifolds[i]      
      node1 = cm.getNode0()
      sector_transition_node = cm.getNode1()      
      col_mask1 = node1.getIntoCollideMask().getLowestOnBit()
      col_mask2 = sector_transition_node.getIntoCollideMask().getLowestOnBit()
      
      if (col_mask2 != CollisionMasks.SECTOR_TRANSITION.getLowestOnBit()) or (col_mask1 != CollisionMasks.GAME_OBJECT_ORIGIN.getLowestOnBit()):
        continue
      
      
      processed_contacts.append(i)
      
      src_sector  = self.sectors_dict_[sector_transition_node.getPythonTag(SectorTransition.SOURCE_SECTOR_NAME)]
      dest_sector = self.sectors_dict_[sector_transition_node.getPythonTag(SectorTransition.DESTINATION_SECTOR_NAME)]
      id = node1.getPythonTag(GameObject.ID_PYTHON_TAG)
      obj = self.game_object_map_.get(id,None)
            
      if obj is None:
        logging.warn('Object with game id %s was not found')
        continue
      
      logging.debug("Sector Transition detected from src: %s to dest: %s"%(src_sector.getName(),dest_sector.getName()))
      
      src_sector.remove(obj)
      dest_sector.attach(obj) 
      src_sector.enableTransitions(False)
      dest_sector.enableTransitions(True)
      break
      
    unprocessed_contacts = [contact_manifolds[i] for i in range(0,num_contacts) if processed_contacts.count(i) == 0]
    return unprocessed_contacts
    
  def __processCollisions__(self):
        
    # processing contacts
    contact_manifolds = self.physics_world_.getManifolds()
    
    unprocessed_contacts = self.__processSectorTransitions__(contact_manifolds)
    
    for r in self.collision_resolvers_:
      unprocessed_contacts = r.processCollisions(unprocessed_contacts,self.game_object_map_,self.mobile_object_ids_)
      
      
        
      
      

      
    
  
  
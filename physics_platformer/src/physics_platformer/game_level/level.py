
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
  __PHYSICS_SIM_STEPSIZE__ = 1.0/80
  
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
    self.dynamic_object_ids_ = [] # list of object ids far all mobile objects
    self.id_counter_ = 0
    self.collision_action_matrix_ = CollisionActionMatrix()
    self.platforms_ = {}  # @brief not really used but might be convenient to hold this list 
    
    # collision handling
    self.collision_resolvers_ = []
    
    # sectors
    self.sectors_dict_ = {}
    self.sectors_list_ = []
    self.active_sector_ = None
    
    self.__createLevelBounds__()
    self.__setupCollisionRules__()
    
  def getPhysicsWorld(self):
    return self.physics_world_
    
  def __del__(self):  
    
    self.detachNode()  
    
    # removing game objects
    for gobj in self.game_object_map_.values():
      gobj.clearPhysicsWorld()
    
    # removing all remaining objects from physics world
    objs = self.physics_world_.getRigidBodies() 
    num_objects = len(objs)
    for obj in objs:          
      self.physics_world_.remove(obj)
      logging.debug('Removed Game Object %s'%(obj.getName()))
      
    objs = self.physics_world_.getConstraints() 
    num_objects = len(objs)
    logging.debug('Removing %i constraints from level %s\'s physics world' % (num_objects,self.getName()))
    for obj in objs:     
      self.physics_world_.remove(obj)
    
    objs = self.physics_world_.getGhosts() 
    num_objects = len(objs)
    logging.debug('Removing %i ghosts bodies from level %s\'s physics world '%(num_objects,self.getName()))
    for obj in objs:     
      self.physics_world_.remove(obj)
          
    if not self.isSingleton(): 
      num_objects = self.getNumChildren()
      for i in range(0,num_objects):
        np = self.getChild(i)        
        logging.debug('Level {0} detaching rogue node {1}'.format(self.getName(),np.getName()))
        np.detachNode()
        
      
    self.game_object_map_ = {}
    self.platforms_ = {}
    
    logging.debug('Level {0} cleaup done'.format(self.getName()))
    
  def createSector(self,transform, name = ''):    
    
    name = name if len(name) > 0 else self.getName() + '-sector-' + str(len(self.sectors_dict_))     
    if name in self.sectors_dict_:
      logging.warn("Sector {0} already in level".format(name))
      return None
       
    sector = Sector(name,self,self.physics_world_,transform)
    self.sectors_dict_[sector.getName()] = sector
    self.sectors_list_.append(sector)
    return sector
    
  def getSectors(self):
    return self.sectors_list_
  
  def getSector(self, name):
    if name in self.sectors_dict_:
      return self.sectors_dict_.get(name); 
    else:
      logging.error("No sector with name %s was found"%(name))
      return None
    
  def addCollisionResolver(self,resolver):
    """
    Adds a collision resolver which will be invoked on every update in order to resolve collisions between 
    the various objects in the level
    """
    resolver.setupCollisionRules(self.physics_world_)
    self.collision_resolvers_.append(resolver)
    
  def addPlatform(self,platform):            
    self._registerGameObj_(platform, False, True)
    self.platforms_[platform.getObjectID()] = platform
    
  def addGameObject(self,game_object, is_dynamic = True):      
    self._registerGameObj_(game_object, is_dynamic, True)
    
  def hasGameObject(self,game_object):    
    obj_name = ''
    if isinstance(game_object, GameObject):
      obj_name = game_object.getName()    
    elif isinstance(game_object, str):
      obj_name = game_object
    else:
      raise ValueError('Object is of unknown type, it should be either a string or GameObject')
    
    if obj_name in self.game_object_map_:
      return True    
    return False
        
  def _registerGameObj_(self,game_object, is_dynamic, add_to_physics,reparent = True ):    
    """
    @brief Adds and object and its children to the level's internal buffers for tracking 
            and to the physics world
    """
    if not isinstance(game_object, GameObject):
      logging.error('Object {0} is not an instance of GameObject'.format(game_object.getName()))
      return False
    
    if game_object.getName() in self.game_object_map_:
      logging.warn('Object {0} already added to Level {1}, skipping'.format(game_object.getName(),self.getName()))
      return True
    
    if reparent:  
      game_object.reparentTo(self) 
      
    self.game_object_map_[game_object.getName()] = game_object    
    if add_to_physics:
      game_object.setPhysicsWorld(self.physics_world_)    
    
    self.id_counter_+=1
    
    if is_dynamic and (game_object.getName() not in self.dynamic_object_ids_): 
      self.dynamic_object_ids_.append(game_object.getName())     
      
    for obj in game_object.getChildrenGameObjects():
      # Not adding to physics since the parent's setPhysicsWorld() method
      # should've added them.  Not reparenting to the level either.
      if not self._registerGameObj_(obj, is_dynamic, False,False):
        return False
    
    logging.debug("\tAdded {0} to level {1}".format(game_object.getName(),self.getName()))
    return True
      
  
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
    self.physics_world_.setGroupCollisionFlag(CollisionMasks.SECTOR_TRANSITION.getLowestOnBit(),CollisionMasks.ACTION_TRIGGER_0.getLowestOnBit(),True)
    
  def __processSectorTransitions__(self,contact_manifolds):  
    processed_contacts = []
    
    num_contacts = len(contact_manifolds)
    for i in range(0,num_contacts):
      
      cm = contact_manifolds[i]      
      node1 = cm.getNode0()
      sector_transition_node = cm.getNode1()      
      col_mask1 = node1.getIntoCollideMask().getLowestOnBit()
      col_mask2 = sector_transition_node.getIntoCollideMask().getLowestOnBit()
      
      if (col_mask2 != CollisionMasks.SECTOR_TRANSITION.getLowestOnBit()) or (col_mask1 != CollisionMasks.ACTION_TRIGGER_0.getLowestOnBit()):
        continue
      
      
      processed_contacts.append(i)
      
      id = node1.getName()
      obj = None
      if id in self.game_object_map_:
        obj = self.game_object_map_.get(id,None)          
      else:
        id_obj = node1.getPythonTag(GameObject.ID_PYTHON_TAG)
        obj = self.game_object_map_.get(id_obj,None) if id_obj is not None else None    
            
      if obj is None:
        logging.warn('Object with game id %s was not found'%(id))
        continue    
      
      src_sector  = self.sectors_dict_[obj.getReferenceNodePath().getName()]
      dest_sector = self.sectors_dict_[sector_transition_node.getPythonTag(SectorTransition.DESTINATION_SECTOR_NAME)]
      entrance_pos = sector_transition_node.getPythonTag(SectorTransition.ENTRANCE_POSITION)
      
      logging.debug("Sector Transition detected from src: %s to dest: %s"%(src_sector.getName(),dest_sector.getName()))
      
      src_sector.enableTransitions(False)
      src_sector.remove(obj)      
      dest_sector.attach(obj,entrance_pos) 
      dest_sector.enableTransitions(True)
      break
      
    unprocessed_contacts = [contact_manifolds[i] for i in range(0,num_contacts) if processed_contacts.count(i) == 0]
    return unprocessed_contacts
    
  def __processCollisions__(self):
        
    # processing contacts
    contact_manifolds = self.physics_world_.getManifolds()
    
    unprocessed_contacts = self.__processSectorTransitions__(contact_manifolds)
    
    for r in self.collision_resolvers_:
      unprocessed_contacts = r.processCollisions(unprocessed_contacts,self.game_object_map_,self.dynamic_object_ids_)
      
      
        
      
      

      
    
  
  
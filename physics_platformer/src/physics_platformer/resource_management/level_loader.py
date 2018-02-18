import sys
import logging
import rospkg
import getopt
import os
from panda3d.core import NodePath, GeomNode, Point3, LPoint3, LVecBase3
from panda3d.core import PandaNode
from panda3d.core import loadPrcFileData
from panda3d.core import Vec3
from panda3d.core import ModelPool
from panda3d.core import Filename

from physics_platformer.game_object import GameObject
from physics_platformer.game_level import *
from physics_platformer.collision import *
from physics_platformer.resource_management.assets_common import *
from panda3d.bullet import BulletTriangleMesh, BulletRigidBodyNode,\
  BulletTriangleMeshShape, BulletGhostNode




  
class LevelLoader(object):
  
  # Supported extensions
  EGG_EXTENSION = '.egg'
  
  def __init__(self):
    self.level_ = None
    self.start_position_np_ = None
  
  def load(self, file_path, verbosity = False):
    """
    @details This function loads an entire level from an egg file provided that it has been
    structured in accordance to the level representation of this library.  The egg
    file can be entirely created in blender and exported to egg with the YABEE addon
    https://github.com/09th/YABEE
    
    @param file_path A string with the path to the resource
    @param verbosity Print extra info about the loaded model file
    @return The loaded Level object
    """
    
    # set logging level
    log_level = logging.INFO    
    current_logging_level = logging.getLogger().getEffectiveLevel()
    if verbosity:
      log_level = logging.DEBUG
      
    logging.basicConfig(format='%(levelname)s: %(message)s',level=log_level)  
    
    class ScopeExit(object):
      def __init__(self,logging_level):
        self.loggin_level = logging_level
        
      def __enter__(self):
        return self
      
      def __exit__(self,exc_type,exc_value,traceback):
        logging.basicConfig(format='%(levelname)s: %(message)s',level=self.loggin_level)  
        return True
      
    with ScopeExit(current_logging_level) as sc:
    
      # check extension
      valid_extensions = [LevelLoader.EGG_EXTENSION]
      file_path = os.path.normpath(file_path)
      found_ext =''
      for ext in valid_extensions:      
        if file_path.endswith(ext):
          found_ext = ext    
          break
        
      if found_ext == '':
        logging.error("The file %s is not supported, only %s are currently supported"%(file_path, str(valid_extensions)))
        return None
        
      # loading file
      model_np = None
      if found_ext is LevelLoader.EGG_EXTENSION:      
        model_np = LevelLoader._readEggFile_(file_path)
        
      if model_np is None:
        logging.error("Failed to load the %s file"%(file_path))
        return None
      else:
        logging.info("Loaded the resource file %s"%(file_path))
      
      # loading model into level
      level_name = model_np.getName()  # it is assume that the top level node is the level node
      level_name.replace(ext,'')
      self.level_ = Level(level_name,min_point = Vec3(-150,-150,-50),max_point = Vec3(150,150,100))
      
      if model_np.getNumChildren() == 0:
        logging.error('Model in file is empty')
        return None
      
      # momentarily setting level as parent of model
      #model_np.reparentTo(self.level_)
      self.model_np_ = model_np
      
      node_names = [n.getName() for n in model_np.getChildren()]
      logging.debug(str(node_names))
      
      for model_child_np in model_np.getChildren():      
  
  
        if not self._loadObject_(model_child_np):        
          logging.error('Failed to load model "{0}"'.format(model_child_np.getName()))
          return None
      
    return self.level_
      
    
    def _writeModelTree_(np):
      
      def toTabChars(indentation_level):
        t = '  '
        return t*indentation_level
      
      depth = 0
      def writeNode(np,depth):
        name = np.getName()
        tags = np.getTagKeys()
        
        info = toTabChars(depth) + '-' + np.getName()        
        depth +=1
        
        if len(tags) > 0:
          info += '\n' + toTabChars(depth + 1) + 'Tags:'
          for tag in tags:
            info += '\n' + toTabChars(depth + 2) + '[%s : %s]'%(tag,str(np.getTag(tag)))
            
          info += '\n'
          
        if np.getNumChildren() > 0:
          for model_child_np in np.getChidren():
            into += '\n' + writeNode(model_child_np,depth)
            
        return info
      
      return writeNode(np,depth)
    
  
  @staticmethod
  def _readEggFile_(file_path):
    
    # loading egg model
    model_root = ModelPool.loadModel(Filename(file_path))
    return NodePath(model_root) if model_root is not None else None
  
  def _loadObject_(self,model_np):
    
    
    """
      # high level elements
      START_LOCATION            = 6
      SECTOR                    = 7
      SECTOR_TRANSITION         = 9
      SECTOR_ENTRY_LOCATION        = 10
      STATIC_PLATFORM           = 11
      
      # collision objects
      COLLISION_PLATFORM_RB     = 111
      COLLISION_LEDGE_RIGHT     = 112
      COLLISION_LEDGE_LEFT      = 114
      COLLISION_SURFACE         = 115
      COLLISION_WALL            = 116
      COLLISION_CEILING         = 117
      
      # visual elements
      VISUAL_OBJECT             = 211
    """  
    
    if not model_np.hasTag(CustomProperties.OBJECT_TYPE_INT):
      logging.warn('Model node "{0}" skipped'.format(model_np.getName()))
      return True    
    
    obj_type = self._getObjType_(model_np)
    if obj_type is None:
      logging.error('Failed to read "{0}" property from model node {1}'.format(CustomProperties.OBJECT_TYPE_INT,child_np.getName()))
      return False
    
    parent_np = model_np.getParent()
    loaded_obj = True
    if obj_type == ObjectTypeID.STATIC_PLATFORM:
      if not self._loadPlatform_(model_np):
        return False        
      
    elif obj_type == ObjectTypeID.SECTOR:
      if not self._loadSector_(model_np):
        return False
      
    elif obj_type == ObjectTypeID.START_LOCATION:
      # TODO: Create a class for this type of object,
      #      It should have a method to set the characters location
      #      and attach it to a sector
      pass
      
    elif obj_type == ObjectTypeID.COLLISION_LEDGE_LEFT or  \
        obj_type == ObjectTypeID.COLLISION_LEDGE_RIGHT:
      if not self._loadLedge_(model_np):
        return False
    else:
      loaded_obj = False
      
    if loaded_obj:      
      logging.info(' - Loaded {0} model as {1} game object type'.format(model_np.getName(), obj_type))
      
    # loading children game objects    
    for model_child_np in model_np.getChildren():
      if self.level_.hasGameObject(model_child_np.getName()):
        logging.warn('Model {0} is already a GameObject in the Level {1}'.format(
          model_child_np.getName(),self.level_.getName()))
        continue
      
      if not self._loadObject_(model_child_np) :
        return False   
    
    return True
  
  def _loadSector_(self, np):
    parent_np = np.getParent()
    tr = np.getTransform(parent_np)
    sector = self.level_.createSector(tr,np.getName())
    
    if sector is None:
      logging.error('Failed to load model %s as a sector'.format(np.getName()))
      return False
    
    sector.setTransform(self.level_,tr);
    return True
  
  def _loadPlatform_(self, np):
    """
    Loads a platform object from the node path
    @param np   NodePath containing the platform nodes (Geometries, ledges and other ghost nodes for walls, floor, etc.)
    @return True if succeeded, false otherwise
    """
    
    parent_np = np.getParent()
    
    # finding node path containing platform rigid body
    if np.getNumChildren() == 0:
      logging.error("Plaform node has no children")
      return False
    platform_np_list = []
    other_np_list = []
    
    for child_np in np.getChildren():
      
      obj_type = self._getObjType_(child_np)
      if obj_type is None:
        logging.error('Failed to read "{0}" property from model node {1}'.format(CustomProperties.OBJECT_TYPE_INT,child_np.getName()))
        return False
      
      if obj_type == ObjectTypeID.COLLISION_PLATFORM_RB:
        platform_np_list.append(child_np)
      else:
        other_np_list.append(child_np)
        
    
    if len(platform_np_list) == 0:
      logging.error("Platform %s rigid body node(s) not found"%(np.getName()))
      return False
    else:
      logging.debug("Platform  {0} has {1} rigid bodies".format(np.getName(),len(platform_np_list)))
    
    # creating rigid body
    bullet_rb_node = BulletRigidBodyNode(np.getName())
    for platform_rb_np in platform_np_list:
      
      bt_shape = self._createBulletShape_(platform_rb_np,True,False) # applying scaling only
      if bt_shape is None:
        return False
      tr = platform_rb_np.getTransform(np)
      tr = tr.setScale(LPoint3(1,1,1))
      bullet_rb_node.addShape(bt_shape,tr);
    
    # instantiate platform
    platform = Platform(bullet_rb_node);    
    
    # TODO: temporarity adding collision model nodes for visualization
    for platform_rb_np in platform_np_list:
      tr = platform_rb_np.getTransform(np)
      platform_rb_np.reparentTo(platform)
      platform_rb_np.setTransform(platform,tr)   
      
    # placing platform as child of level
    platform.reparentTo(self.level_)
    tr = np.getTransform(parent_np)
    platform.setTransform(self.level_,tr)
    
    # find ledges and other objects
    for child_np in other_np_list:
      loaded_ok = True
      obj_type = LevelLoader._getObjType_(child_np)
      
      if obj_type == ObjectTypeID.COLLISION_LEDGE_RIGHT or obj_type == ObjectTypeID.COLLISION_LEDGE_LEFT:
        loaded_ok = self._loadLedge_(child_np,platform)
        
      
      elif obj_type == ObjectTypeID.COLLISION_WALL:     
        loaded_ok = self._loadGhostNode_(child_np,platform,CollisionMasks.WALL)            
        
      elif obj_type == ObjectTypeID.COLLISION_SURFACE:
        loaded_ok = self._loadGhostNode_(child_np,platform,CollisionMasks.SURFACE)
        
      elif obj_type == ObjectTypeID.COLLISION_CEILING:
        loaded_ok = self._loadGhostNode_(child_np,platform,CollisionMasks.CEILING)
        
      if not loaded_ok:
        return False
      
    # Do this at the end to add newly added ghost nodes to the physics world
    self.level_.addPlatform(platform)    
  

    return True
  
  def _loadLedge_(self,np, new_parent = None):
    
    if new_parent is None:
      new_parent = self.level_
    
    parent_np = np.getParent()
    obj_type = LevelLoader._getObjType_(np)
    if (obj_type != ObjectTypeID.COLLISION_LEDGE_RIGHT) and (obj_type != ObjectTypeID.COLLISION_LEDGE_LEFT):
      logging.error("Node %s does not contain a Ledge Game Object"%(np.getName()))
      return False
    

    
    # calculating dimensions
    bounding_vol = np.getTightBounds()
    minp = bounding_vol[0]
    maxp = bounding_vol[1]
    extends = maxp - minp
    size_ = [extends.getX(), extends.getY(), extends.getZ()]
    
    # verifying non-zero dimensions
    size_vec = None
    if all(x > 0 for x in size_):
      width_ = min(size_)
      length_ = max(size_)
      size_vec = Vec3(width_,length_,size_[2])  
    else:
      logging.error("Ledge Size vector is zero")
      return False            
    
    
    # creating ledge but ignoring dimensions for now
    is_right_ledge = True if obj_type == ObjectTypeID.COLLISION_LEDGE_RIGHT else False
    ledge_obj = Ledge(np.getName(),is_right_ledge,size_vec)
    
    # adding ledge to level    
    self.level_.addGameObject(ledge_obj,False)
    
    # getting relative transform
    pos = np.getPos(parent_np)
    ledge_obj.setPos(new_parent,pos)      
      
    return True
  
  def _loadBtRigidBodyNode_(self,np):
    pass    
  
  def _loadStartPosition_(self,np):
    pass
  
  def _loadGhostNode_(self,np,new_parent_np, col_mask):
    
    parent_np = np.getParent()
    bt_ghost = self._createBtGhostNode_(np)
    
    bt_ghost_np = None
    if bt_ghost is not None:        
      bt_ghost_np = new_parent_np.attachNewNode(bt_ghost)
      
      # applying local transform
      tr = np.getTransform(parent_np)
      tr = tr.setScale(LPoint3(1))  # dissmissing local scaling
      bt_ghost_np.setTransform(new_parent_np,tr)
      
      # set collision mask
      bt_ghost_np.node().setIntoCollideMask(col_mask)
    else:
      logging.error("Failed to load %s into a ghost node"%(np.getName()))
      return False 
    
    return True
    
  
  def _createBtGhostNode_(self,np):
    """
    @brief Creates a Bullet Ghost node from the shapes in the model node.  Ignores
    any local geometry transforms but applies local scaling encoded in the model node.
    """
    bt_shape = self._createBulletShape_(np,True,False)
    if bt_shape is None:
      return None
    
    bt_ghost = BulletGhostNode(np.getName())
    bt_ghost.addShape(bt_shape)      
    return bt_ghost
    
    
  
  def _createBulletShape_(self,np, apply_scale = True, apply_transform = True):
    """
    @brief Creates a BulletTriangleMeshShape from the geometries in the model node.  The passed
    node path must point to a GeomNode type.  The Geom objects are then added to a 
    BulletTriangleMesh object which is then used to initialize the Shape.  Optionally, 
    the node's transform and scaled can be baked into the Geometries (recommended 
    according to the Panda3D guide https://www.panda3d.org/manual/index.php/Bullet_FAQ).
    If you apply the scale and transform make sure not to apply them again to the shape or
    the bullet node that contains the shape as it'll compound the effect.
    @warning: If the underlying GeomNode contains multiple geometries each with a different
    transform and scale then it's best to set apply_scale and apply_transform to True.
    @param np: The nodepath containing the GeomNode
    @param apply_scale: Boolean that allows choosing whether or not to apply the nodepath's scale to the geometries
    @param apply_transform: Boolean that indicates whether or not to apply the nodepath's trasform to the geometries.
    @return:  A BulletTriangleMeshShape object containing the node's geometries
    """
    
    geom_node = np.node()
    if type(geom_node) is not GeomNode:
      logging.error("Node %s is not a GeomNode node type"%(np.getName()))
      return None
    
    bullet_mesh = BulletTriangleMesh()
        
    # Assembling transform
    tr = TransformState.makeIdentity()
    geom_scale = np.getScale()
    if apply_transform:
      tr = tr.setPos(np.getPos())
      tr = tr.setQuat(np.getQuat())
      sc = LPoint3(1)
      tr = tr.setScale(sc)
    if apply_scale: # baking scale into geometry data
      tr = tr.setScale(geom_scale)    

    for geom in geom_node.getGeoms():      
      bullet_mesh.addGeom(geom,True,tr)
    
    return BulletTriangleMeshShape(bullet_mesh,False,True,True)
  
  @staticmethod
  def _getObjType_(np):
    obj_type = 0
    try:
      obj_type = int(float(np.getTag(CustomProperties.OBJECT_TYPE_INT)))
    except ValueError as e:
      logging.error(str(e))
      return None
    return obj_type
    
  

  
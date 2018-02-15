import sys
import logging
import rospkg
import getopt
import os
from panda3d.core import NodePath, GeomNode, Point3
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


EGG_EXTENSION = '.egg'

  
class LevelLoader(object):
  
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
    """
    
    # check extension
    valid_extensions = [EGG_EXTENSION]
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
    if found_ext is EGG_EXTENSION:      
      model_np = __readEggFile__(file_path)
      
    if model_np is None:
      logging.error("Failed to load the %s file"%(file_path))
      return None
    else:
      logging.info("Loaded the resource file %s"%(file_path))
    
    # loading model into level
    level_name = model_np.getName()  # it is assume that the top level node is the level node
    level_name.replace(ext,'')
    self.level_ = Level(level_name)
    
    if model_np.getNumChildren() == 0:
      logging.error('Model in file is empty')
      return None
    
    for cnp in model_np.getChildren():
      
      if not cnp.hasTag(CustomProperties.OBJECT_TYPE_INT):
        continue
      
      obj_type = int(cnp.getTag(CustomProperties.OBJECT_TYPE_INT))
      
      """
        # high level elements
        START_POSITION            = 6
        SECTOR                    = 7
        SECTOR_TRANSITION         = 9
        SECTOR_ENTRY_POINT        = 10
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
      
      parent_np = model_np
      if obj_type == ObjectTypeID.STATIC_PLATFORM:
        tpl = self.__loadPlatform__(cnp)
        if tpl is None:
          return False
        
        platform, rel_tr = tpl        
        self.level_.addPlatform(platform)
        platform.setTransform(self.level_,rel_tr)
        
      if obj_type == ObjectTypeID.SECTOR:
        tr = cnp.getTransform(parent_np)
        self.level_.addSector(tr,cnp.getName())
        
      if obj_type == ObjectTypeID.START_POSITION:
        tr = cnp.getTransform(parent_np)
        self.cnp.reparentTo(self.level_)
        self.cnp.setTransform(tr)
        self.start_position_np_ = cnp
        
      if obj_type == ObjectTypeID.COLLISION_LEDGE_LEFT or obj_type == ObjectTypeID.COLLISION_LEDGE_RIGHT:
        tpl = self.__loadLedge__(cnp)
        if tpl is None:
          return False
        ledge, rel_tr = tpl
        self.level_.addGameObject(ledge,is_dynamic = False)
        level.setTransform(self.level_,rel_tr)
      
    
    def __writeModelTree__(np):
      
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
          for cnp in np.getChidren():
            into += '\n' + writeNode(cnp,depth)
            
        return info
      
      return writeNode(np,depth)
    
    
    @staticmethod
    def __readEggFile__(file_path):
      
      # loading egg model
      model_root = ModelPool.loadModel(Filename(file_path))
      return NodePath(model_root) if model_root is not None else None
    
    def __loadSector__(self, np):
      pass
    
    def __loadPlatform__(self, np, parent_np):
      """
      Loads a platform object from the node path
      @param np   NodePath containing the platform nodes (Geometries, ledges and other ghost nodes)
      @param parent_np Parent of np, usually a sector node path
      @return True if succeeded, false otherwise
      """
      
      # finding node path containing platform rigid body
      if np.getNumChildren() == 0:
        logging.error("Plaform node has no children")
        return False
      platform_np_list = []
      other_np_list = []
      for chid_np in np.getChildren():
        obj_type = int(chid_np.getTag(CustomProperties.OBJECT_TYPE_INT))
        if obj_type == ObjectTypeID.COLLISION_PLATFORM_RB:
          platform_np_list.append(chid_np)
        else:
          other_np_list.append(chid_np)
          
      
      if len(platform_np_list) == 0:
        logging.error("Platform %s rigid body node(s) not found"%(np.getName()))
        return False
      
      # creating rigid body
      bullet_rb_node = BulletRigidBodyNode(np.getName())
      for platform_rb_np in platform_np_list:
        
        bt_shape = self.__getBulletShape__(platform_rb_np)
        if bt_shape is None:
          return False
        
        bullet_rb_node.addShape(bt_shape);
      
      # instantiate platform
      platform = Platform(bullet_rb_node);
      
      
      # find ledges and other objects
      for child_np in other_np_list:
        loaded_ok = True
        obj_type = int(chid_np.getTag(CustomProperties.OBJECT_TYPE_INT))
        if obj_type == ObjectTypeID.COLLISION_LEDGE_RIGHT:
          loaded_ok = self.__loadLedge__(chid_np, platform)
          
        elif obj_type == ObjectTypeID.COLLISION_LEDGE_LEFT:
          loaded_ok = self.__loadLedge__(chid_np, platform)
          
        elif obj_type == ObjectTypeID.COLLISION_WALL:
          
          bt_ghost = self.__getBtGhostNode__(chid_np,CollisionMasks.WALL)
          if bt_ghost is not None:
            bt_ghost_np = platform.attachNewNode(bt_ghost)
            tr = chid_np.getTransform(np)
            bt_ghost_np.setTransform(platform,tr)
          else:
            loaded_ok = False
            logging.error("Failed to load %s into a ghost node"%(chid_np.getName()))
            
          
        elif obj_type == ObjectTypeID.COLLISION_SURFACE:
          loaded_ok = self.__loadBtGhostNode__(chid_np,platform)
          
        elif obj_type == ObjectTypeID.COLLISION_CEILING:
          loaded_ok = self.__loadBtGhostNode__(chid_np,platform)
          
        if not loaded_ok:
          return False
          

      return True
    
    def __loadLedge__(self,np,parent_np):
      
      obj_type = int(np.getTag(CustomProperties.OBJECT_TYPE_INT))
      if (obj_type != ObjectTypeID.COLLISION_LEDGE_RIGHT) and (obj_type != ObjectTypeID.COLLISION_LEDGE_LEFT):
        logging.error("Node %s does not contain a Ledge Game Object"%(np.getName()))
        return False
      
      # getting relative transform
      tr = np.getTransform(parent_np)
      
      # calculating dimensions
      minp = maxp = Point3()
      np.calcTightBounds(min, max)
      extends = maxp - minp
      size_ = [extends.getX(), extends.getY(), extends.getZ()]
      
      # verifying non-zero dimensions
      size_vec = None
      if all(x > 0 for x in size_):
        width_ = min(size_)
        length_ = max(size_)
        size_vec = Vec3(width_,length_,size_[2])        
      
      
      # creating ledge but ignoring dimensions for now
      is_right_ledge = true if obj_type == ObjectTypeID.COLLISION_LEDGE_RIGHT else False
      ledge_obj = Ledge(np.getName,is_right_ledge,size_vec)
      
      # adding ledge to level
      self.level_.addGameObject(ledge_obj,False)
      ledge_obj.setTransform(parent_np,tr)
      
        
      return True
    
    def __loadBtRigidBodyNode__(self,np):
      pass
    
    def __getBtGhostNode__(self,np,col_mask):
      bt_shape = self.__getBulletShape__(np)
      if bt_shape is None:
        return None
      
      bt_ghost = BulletGhostNode(np.getName())
      bt_ghost.addShape(bt_shape)
      bt_ghost.setIntoCollideMask(col_mask)
      return bt_ghost
      
      
    
    def __getBulletShape__(self,np):
      
      geom_node = np.node()
      if type(geom_node) is not GeomNode:
        logging.error("Node %s is not a GeomNode node type"%(np.getName()))
        return None
      
      bullet_mesh = BulletTriangleMesh()
      for geom in geom_node.getGeoms():
        bullet_mesh.addGeom(geom,true)
      
      return BulletTriangleMeshShape(bullet_mesh)
      
    
    def __loadStartPosition__(self,np):
      pass
    
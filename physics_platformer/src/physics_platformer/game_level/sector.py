import sys
import logging

from panda3d.core import NodePath, TransformState, PandaNode, LQuaternion, Vec3
from panda3d.bullet import BulletRigidBodyNode, BulletPlaneShape,\
  BulletGhostNode, BulletBoxShape, BulletGenericConstraint
from physics_platformer.collision import CollisionMasks
from physics_platformer.game_object import GameObject

class SectorTransition(NodePath):
  
  SOURCE_SECTOR_NAME = 'SOURCE_SECTOR'
  DESTINATION_SECTOR_NAME = 'DESTINATION_SECTOR'
  
  def __init__(self,name,size,src_sector_name,destination_sector_name):
    
    NodePath.__init__(self,BulletGhostNode(name))
    self.src_sector_name_ = src_sector_name
    self.destination_sector_name_ = destination_sector_name    
    self.node().addShape(BulletBoxShape(size/2))
    self.node().setIntoCollideMask(CollisionMasks.SECTOR_TRANSITION)
    self.setPythonTag(SectorTransition.SOURCE_SECTOR_NAME, self.src_sector_name_)
    self.setPythonTag(SectorTransition.DESTINATION_SECTOR_NAME, self.destination_sector_name_)
    
  def getDestinationSectionName(self):
    return self.destination_sector_name_
  
  def getSourceSectorName(self):
    return self.src_sector_name
  
  def setEnabled(self,enable):    
    self.node().setIntoCollideMask(CollisionMasks.SECTOR_TRANSITION if enable else CollisionMasks.NO_COLLISION)

class Sector(NodePath):
  
  SECTOR_TRANSITION_SIZE = Vec3(1,2,10)
  
  def __init__(self,name,parent_np , physics_world, tr = TransformState.makeIdentity()):
    """
    Sector(NodePath parent_np, TransformState tr = TransformState.makeIdentity()
    
      Creates a level Sector object which ensures that all objects in it only move in the x and z
      directions relative to the sector.
      
      @param parent_np: NodePath to the parent of the sector, usually is the Level object that contains the sector.
      @param physics_world: The physics world
      @param tf: Transform of the sector relative to the parent_np NodePath
    """
    
    NodePath.__init__(self,name)
    self.reparentTo(parent_np)    
    self.setTransform(self,tr)
    self.physics_world_ = physics_world
    
    # creating 2d motion plane
    self.motion_plane_np_ = self.attachNewNode(BulletRigidBodyNode())
    self.motion_plane_np_.node().setMass(0)
    self.motion_plane_np_.node().setIntoCollideMask(CollisionMasks.NO_COLLISION)
    self.motion_plane_np_.node().addShape(BulletPlaneShape(Vec3(0,1,0),0))
    self.physics_world_.attach(self.motion_plane_np_.node())
    self.motion_plane_np_.reparentTo(parent_np)
    self.motion_plane_np_.setTransform(self,TransformState.makeIdentity())
    
    # game objects
    self.object_constraints_dict_ = {} # stores tuples of the form (String,BulletConstraint)
    
    # sector transitions
    self.sector_transitions_ = []
    self.destination_sector_dict_ = {}
    
  def __del__(self):
    
    for k,c in self.object_constraints_dict_.items():
      self.physics_world_.remove(c)
    self.object_constraints_dict_.clear()
      
    # sector transitions
    for s in self.sector_transitions_:
      self.physics_world_.remove(s.node())
    self.sector_transitions_ =[]
    self.destination_sector_dict_ = {}
      
    self.physics_world_.remove(self.motion_plane_np_.node())
         
    
  def addTransition(self,destination_sector,pos, on_right_side ,size = None):
    """
    addAdjacentSector(Sector sector, Vec3 pos, Vec3 size = None)
      Creates a transition that connects this sector to a destination_sector
      
      @param destination_sector: Destination sector object.
      @param pos: Position of transition point relative to this sector.
      @param on_right_side:  Whether the transition node box is placed to the right or left side of the transition point.
      @param size: Size of the transition detector region.
    """
    
    size = Sector.SECTOR_TRANSITION_SIZE if size is None else size
    
    st = SectorTransition(self.getName() + '-transition-to-' + destination_sector.getName(),
                          size,
                          self.getName(),
                          destination_sector.getName())
    
    width = size[0]
    height = size[2]
    direction = 1 if on_right_side else -1
    
    st.reparentTo(self)
    st_pos = Vec3(pos.getX()+ direction*(width/2 + 4*GameObject.ORIGIN_SPHERE_RADIUS),0,pos.getZ()+ 0.5*height)
    st.setPos(self,st_pos)
    self.physics_world_.attach(st.node())
    
    self.sector_transitions_.append(st)
    self.destination_sector_dict_[st.getName()] = destination_sector
    st.setEnabled(False)
    
    logging.debug('Sector Transition added from %s to %s at position %s to the %s'%(self.getName(),
                                                                                   destination_sector.getName(),str(pos),'right' if on_right_side else 'left'))
    
    
    
  def enableTransitions(self,enable):
    for st in self.sector_transitions_:
      st.setEnabled(enable)
    
  def getAdjacentSector(self,transition_np_name):
    """
    getAdjacentSector(String transition_np_name)
      returns the Sector corresponding to the transition nodepath.
    """
    return self.destination_sector_dict_.get(transition_np_name,None)
    
    
  def attach(self,obj):
    
    if not self.motion_plane_np_.getTransform(self).isIdentity():
      self.motion_plane_np_.setTransform(self,TransformState.makeIdentity())
    
    constraint = self.__create2DConstraint__(obj)
    self.physics_world_.attach(constraint)
    constraint.setEnabled(True)
    self.object_constraints_dict_[obj.getObjectID()] = constraint
    obj.setReferenceNodePath(self)
      
  def remove(self,obj):
    
    if not self.object_constraints_dict_.has_key(obj.getObjectID()):
      return
    
    constraint = self.object_constraints_dict_[obj.getObjectID()]
    constraint.setEnabled(False)
    self.physics_world_.remove(constraint)
    obj.setReferenceNodePath(None)
    del self.object_constraints_dict_[obj.getObjectID()]
  
  def __create2DConstraint__(self,obj):
    
    obj.setQuat(self,LQuaternion.identQuat())
    obj.setY(self,0)
    constraint = BulletGenericConstraint(self.motion_plane_np_.node(),obj.node(),
                                         TransformState.makeIdentity(),TransformState.makeIdentity(),False)
    max_float = sys.float_info.max
    constraint.setLinearLimit(0,-max_float,max_float)
    constraint.setLinearLimit(1,0,0)
    constraint.setLinearLimit(2,-max_float,max_float)
    constraint.setDebugDrawSize(0)
    return constraint
    
    
    
    
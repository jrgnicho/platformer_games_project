from panda3d.core import NodePath, TransformState, PandaNode
from panda3d.bullet import BulletRigidBodyNode, BulletPlaneShape,\
  BulletGhostNode, BulletBoxShape
from physics_platformer.collision import CollisionMask
from physics_platformer.game_object import GameObject

class SectorTransition(NodePath):
  
  def __init__(self,name,size,src_sector_name,destination_sector_name):
    
    NodePath.__init__(BulletGhostNode(name))
    self.src_sector_name_ = src_sector_name
    self.destination_sector_name_ = destination_sector_name    
    self.node().addShape(BulletBoxShape(size/2))
    self.node().setIntoCollisionMask(CollisionMask.SECTOR_TRANSITION)
    
  def getDestinationSectionName(self):
    return self.destination_sector_name_
  
  def getSourceSectorName(self):
    return self.src_sector_name

class Sector(NodePath):
  
  SECTOR_TRANSITION_SIZE = Vec3(1,1,2)
  
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
    self.motion_plane_np_.node().setIntoCollideMask(CollisionMask.NONE)
    self.motion_plane_np_.node().addShape(BulletPlaneShape(Vec3(0,1,0),0))
    self.physics_world_.attach(self.motion_plane_np_.node())
    
    # sector transitions
    self.sector_transitions_ =[]
    self.destination_sector_dict_ = {}
    
  def addAdjacentSector(self,destination_sector,pos, size = None):
    """
    addAdjacentSector(Sector sector, Vec3 pos, Vec3 size = None)
      Creates a transition node that connects this sector to Sdestination_sector
      
      @param destination_sector: Destination sector object
      @param pos: Position of transition relative to this sector
      @param size: Size of the transition detector region
    """
    
    size = Sector.SECTOR_TRANSITION_SIZE if size is None else size
    
    st = SectorTransition(self.getName() + '-transition-to-' + destination_sector.getName(),
                          size,
                          self.getName(),
                          destination_sector.getName())
    
    width = size[0]
    direction = 1 if pos.getX() > 0 else -1
    
    st.reparentTo(self)
    st_pos = Vec3(pos.getX()+ direction*(width/2 + 2*GameObject.ORIGIN_SPHERE_RADIUS),0,pos.getZ())
    st.setPos(self,st_pos)
    
    self.sector_transitions_.append(st)
    self.destination_sector_dict_[st.getName()] = destination_sector
    
    
  def attach(self,obj):
    pass
  
  def remove(self,obj):
    pass
  
  def __create2DConstraint__(self,obj):
    pass
    
    
    
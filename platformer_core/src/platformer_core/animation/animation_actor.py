from platformer_core.sprite import Sprite
from platformer_core.sprite import SpriteGroup
from platformer_core.sprite import SpriteSequencePlayer
from platformer_core.sprite import SpriteAnimator
from platformer_core.animation import AnimationInfo
from platformer_core.collision import *
from platformer_core.geometry2d import Box2D
from panda3d.core import NodePath, BoundingVolume
from panda3d.bullet import BulletRigidBodyNode, BulletCapsuleShape, ZUp
from panda3d.bullet import BulletGhostNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletGenericConstraint
from panda3d.core import TransformState
from panda3d.core import SequenceNode
from panda3d.core import Texture
from panda3d.core import Vec3
from panda3d.core import CardMaker
from panda3d.core import BoundingBox
import logging
from panda3d.bullet import BulletRigidBodyNode

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level=logging.INFO)
class AnimationActor(SpriteAnimator):
  
  LOGGER = logging.getLogger(__name__)
  LOGGER.setLevel(level=logging.INFO)
  
  DEFAULT_WIDTH = 0.01
  DEFAULT_MASS = 1.0
  BOUND_PADDING = 0.1
  COLLISION_MARGIN = 0.01
  
  RIGHT_SPRITE_PLAYER_SUFF = '-rsprite-player'
  LEFT_SPRITE_PLAYER_SUFF = '-lsprite-player'
  
  def __init__(self,name,character_name = 'uno', mass = DEFAULT_MASS):
    SpriteAnimator.__init__(self,name)
    
    self.character_name_ = character_name 
    self.mass_ = mass
    self.animation_info_ = None
    self.rigid_body_np_ = None # NodePath to a bullet rigid body that contains the collision boxes that are used to handle interactions with the environment    
    self.action_body_np_ = None # NodePath to a bullet ghost node containing boxes that will be used to trigger a specific player action upon coming into contact with the environment
    self.damage_box_np_ = None # NodePath to a bullet ghost node containing collision boxes that are active during the duration of the animation
    self.hit_box_np_ = None # NodePath to a bullet ghost node containing hit boxes that are active during the duration of the animation
    self.auxiliary_boxes_ = [] # list of Box2d boxes that can be used for a variety of purposes.
    self.parent_physics_world_ = None
    
    # bounds    
    self.rigid_body_bbox_ = None # 2D Bounding box
    self.bbox_top_np_ = None  # Node path to the top box ghost node
    self.bbox_bottom_np_ = None # Node path to the bottom box ghost node
    self.bbox_back_np_ = None # Node path to the rear box ghost node
    self.bbox_front_np_ = None # Node path to the front box ghost node    
   
    # store a reference to itself in order to overcome a limitation with the NodePath 'node()' method
    self.node().setPythonTag(SpriteAnimator.__name__,self)
    
  def setPythonTag(self,tag,obj):
    '''
    Stores a reference of "obj" under the each node's tag including the BulletBodyNode types.
    '''
    SpriteAnimator.setPythonTag(self,tag,obj)       
    for np in [self.rigid_body_np_,self.damage_box_np_,self.hit_box_np_,self.action_body_np_,
               self.bbox_top_np_, self.bbox_front_np_, self.bbox_bottom_np_,self.bbox_back_np_]:
      if np is not None:
        np.setPythonTag(tag,obj)
    
  def loadAnimation(self,animation_info):
    """
    Loads the animation_info data from a AnimationInfo object
    """    
    if type(animation_info) is not AnimationInfo:
      AnimationActor.LOGGER.error("Object pass is not an instance of the AnimationInfo class")
      return False
    
    # load sprites
    if not self.loadAnimationSprites(animation_info.sprites_right, animation_info.sprites_left, animation_info.sprites_time):
      AnimationActor.LOGGER.error('Failed to load sprites from AnimationInfo object')
      return False
    
    # scale    
    scale = (animation_info.scalex, animation_info.scaley)
    
    # saving animation_info
    self.animation_info_ = animation_info
    
    # setting properties
    self.loop_mode_ = animation_info.loop_mode
    self.loop_start_frame_ = animation_info.loopstart
    
    # creating representative rigid body (Used to determine collisions with the environment
    self.__createRigidBody__(scale)
    
    # creating bullet ghost body for detecting interactions with the environment
    if len(self.animation_info_.action_boxes) > 0: # collecting boxes from each individual sprite          
      self.action_body_np_ =  self.rigid_body_np_.attachNewNode(
         self.__createBulletGhostNodeFromBoxes__(self.animation_info_.action_boxes,scale, 
                                                 self.character_name_ + '-' +self.getName() + '-actor-action-gn') )
      self.action_body_np_.node().setIntoCollideMask(CollisionMasks.ACTION_TRIGGER_1)

    # creating attack collision and hit ghosts bodies for handling attack boxes
    col_boxes = []    
    hit_boxes = []
    for elmt in self.animation_info_.animation_elements:
      col_boxes = col_boxes + elmt.damage_boxes
      hit_boxes = hit_boxes + elmt.hit_boxes
      
    if len(col_boxes) > 0:  
      col_boxes = [Box2D.createBoundingBox(col_boxes)]            
      self.damage_box_np_ = self.rigid_body_np_.attachNewNode( 
        self.__createBulletGhostNodeFromBoxes__(col_boxes,scale, self.character_name_ + '-' + self.getName() + '-actor-damage-gn' ) )
      self.damage_box_np_.node().setIntoCollideMask(CollisionMasks.ATTACK_DAMAGE)
      
    if len(hit_boxes) > 0:
      hit_boxes = [Box2D.createBoundingBox(hit_boxes)]
      self.hit_box_np_ = self.rigid_body_np_.attachNewNode( 
        self.__createBulletGhostNodeFromBoxes__(hit_boxes,scale, self.character_name_ + '-' +self.getName() + '-actor-hit-gn'))
      self.hit_box_np_.node().setIntoCollideMask(CollisionMasks.ATTACK_HIT)
      
    # scaling remaining boxes (animation_info frames and auxiliary)     
    self.setScale(Vec3(scale[0],1,scale[1]))
          
    return True
  
  def faceRight(self,face_right = True):
      SpriteAnimator.faceRight(self,face_right)
      
      if (self.bbox_back_np_ is None) or (self.bbox_front_np_ is None):
        return
      
      if face_right:
        self.bbox_back_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_LEFT)
        self.bbox_front_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_RIGHT)
      else:
        self.bbox_back_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_RIGHT)
        self.bbox_front_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_LEFT)
        
    
  def activate(self,physics_world,parent_np):    
    
    self.parent_physics_world_ = physics_world
    if self.rigid_body_np_ is not None:
      self.rigid_body_np_.reparentTo(parent_np)  
      for np in [self.bbox_top_np_, self.bbox_front_np_, self.bbox_bottom_np_,self.bbox_back_np_]:
        self.parent_physics_world_.attach(np.node())
    
    for np in [self.rigid_body_np_,self.damage_box_np_,self.hit_box_np_,self.action_body_np_]:
      if np is not None:
        self.parent_physics_world_.attach(np.node())
        
        
    self.pose(0)
    self.show()  
    
  def deactivate(self):
    
    if self.rigid_body_np_ is not None:
      self.rigid_body_np_.detachNode()
      self.rigid_body_np_.node().clearForces()
      self.rigid_body_np_.node().setLinearVelocity(Vec3(0,0,0))
      for np in [self.bbox_top_np_, self.bbox_front_np_, self.bbox_bottom_np_,self.bbox_back_np_]:
        self.parent_physics_world_.remove(np.node())
    
    if self.parent_physics_world_ is not None:
      for np in [self.rigid_body_np_,self.damage_box_np_,self.hit_box_np_,self.action_body_np_]:
        if np is not None:
          self.parent_physics_world_.remove(np.node())
          
        
    self.stop()
    self.hide()
    
  def getRigidBody(self):
    return (None if (self.rigid_body_np_ is None) else self.rigid_body_np_)
  
  def getRigidBodyBoundingBox(self):
    return self.rigid_body_bbox_
    
  def getDamageBox(self):
    """
    Returns the node path to a ghost body used to determing in an opponent's attack touched the player
    """
    return (None if (self.damage_box_np_ is None) else self.damage_box_np_)
  
  def getHitBox(self):    
    """
    Returns the node path to a ghost body used to determing in player's attack touched the oponent
    """
    return (None if self.hit_box_np_ is None else self.hit_box_np_)
  
  def getActionGhostBody(self):
    """
    Returns ghost body for determining that the action geometry is in overlap
    """
    return self.action_body_np_
    
  def loadAnimationSprites(self,sprites_right, sprites_left,sprites_time):
    """
    loadAnimationSprites
      Loads Sprites for the right and left animations
      Inputs:
      - sprites_right: list[Sprite] list of images for the right side
      - sprites_left: list[Sprite] list of images for the left side
      - sprites_time: list of time values in seconds that each sprite will be shown during an animation 
      - scale: (Vec3) Only the x and z values are used 
    """
    
    if (len(sprites_right) == 0) or (len(sprites_left) == 0):
      AnimationActor.LOGGER.error("ERROR: Found empty image list")
      return False
    
    if len(sprites_right) != len(sprites_left):
      AnimationActor.LOGGER.error("Unequal number of images for the left and right side")
      return False
    
    # storing individual sprite size
    w = sprites_right[0].getXSize() # assumes that all images in the in 'images' array are the same size
    h = sprites_right[0].getYSize()
    self.size_ = (w,h) # image size in pixels
    
    self.seq_right_ = self.__createAnimationSequence__(str(self.getName() )+ AnimationActor.RIGHT_SPRITE_PLAYER_SUFF ,sprites_right,sprites_time,False)
    self.seq_left_ = self.__createAnimationSequence__(str(self.getName() ) + AnimationActor.LEFT_SPRITE_PLAYER_SUFF ,sprites_left,sprites_time,True)
    self.node().addStashed(self.seq_right_)
    self.node().addStashed(self.seq_left_)
    
    self.faceRight(True)     
    
    return True
  
  def setScale(self,scale):
    """
    Sets the scale of the animated sprites, collision and hit boxes in the actor
    """
    SpriteAnimator.setScale(self,Vec3(scale.getX(),1,scale.getZ()))
    
    if self.animation_info_ is None:
      return  
    
    # scaling sprite boxes
    for i in range(0,len(self.animation_info_.sprites_left)):      
      sprt_right = self.animation_info_.sprites_right[i]
      sprt_left = self.animation_info_.sprites_left[i]      
      boxes = sprt_right.hit_boxes + sprt_right.damage_boxes + sprt_left.hit_boxes + sprt_left.damage_boxes
      for box in boxes:
        box.scale = (scale.getX(), scale.getZ())
        
    for box in self.animation_info_.auxiliary_boxes:
      box.scale = (scale.getX(), scale.getZ())
      self.auxiliary_boxes_.append(box)
     
    
  def __createRigidBody__(self,scale):
    self.rigid_body_np_ = NodePath(BulletRigidBodyNode(self.character_name_ + '-' + self.getName()+ '-rb'))
    rigid_body = self.rigid_body_np_.node()
    rigid_body.setIntoCollideMask(CollisionMasks.GAME_OBJECT_RIGID_BODY)
    rigid_body.setFriction(0)
    
    # collection all boxes
    collision_boxes = []
    if len(self.animation_info_.rigid_body_boxes) > 0:      
      # use existing collision boxes 
      collision_boxes = self.animation_info_.rigid_body_boxes
      AnimationActor.LOGGER.info("Using existing rigid body boxes: %s "%( ';'.join(str(x) for x in collision_boxes ) ))
    else:      
      # compute bounding box of all collision boxes from every sprite 
      AnimationActor.LOGGER.warning("Rigid body boxes not found for this animation, creating AABB from damage boxes in all frames")
      boxes = []
      for elemt in self.animation_info_.animation_elements:
        boxes = boxes + elemt.damage_boxes
      
      if len(boxes) > 0:
        collision_boxes = [Box2D.createBoundingBox(boxes)]
        
      
    # create rigid body with capsule shape
    for box in collision_boxes:
      box.scale = scale
      size = box.size
      center = box.center
      transform = TransformState.makeIdentity()
      
      radius = 0.5 * size[0]
      height = size[1] - 2.0* radius
      height = height if height >= 0 else 0.0
      #bullet_collision_shape = BulletBoxShape(Vec3(0.5*size[0],0.5*AnimationActor.DEFAULT_WIDTH,0.5 * size[1]))
      bullet_collision_shape = BulletCapsuleShape(radius,height,ZUp)
      transform = transform.setPos(Vec3(center[0],0,center[1]))
      rigid_body.addShape(bullet_collision_shape,transform)
      
    # completing rigid body setup
    rigid_body.setMass(self.mass_)
    rigid_body.setLinearFactor((1,1,1))   
    rigid_body.setAngularFactor((0,0,0)) 
    rigid_body.setBoundsType(BoundingVolume.BT_box)
    
    # creating bounding box    
    self.rigid_body_bbox_ = Box2D.createBoundingBox(collision_boxes)
    aabb = self.rigid_body_bbox_ 
    
    # creating bounding boxes around rigid body
    offsetx = aabb.center[0]
    offsety = aabb.center[1]
    top = Box2D(aabb.width, AnimationActor.BOUND_PADDING ,(offsetx, offsety + 0.5*aabb.height + 0.5*AnimationActor.BOUND_PADDING))
    bottom = Box2D(aabb.width, AnimationActor.BOUND_PADDING ,(offsetx, offsety - 0.5*aabb.height -0.5*AnimationActor.BOUND_PADDING))
    left = Box2D(AnimationActor.BOUND_PADDING, aabb.height,(offsetx + -0.5*aabb.width - 0.5*AnimationActor.BOUND_PADDING , 
                                                            offsety ))
    right = Box2D(AnimationActor.BOUND_PADDING, aabb.height ,(offsetx + 0.5*aabb.width + 0.5*AnimationActor.BOUND_PADDING ,
                                                            offsety ))
    logging.info("Animation %s Box Center %s"%(self.getName(),str(aabb.center)))
    
    scale = (1,1)
    self.bbox_top_np_ = self.rigid_body_np_.attachNewNode(
      self.__createBulletGhostNodeFromBoxes__([top], scale,self.getName() + '-actor-bbtop-gn'))
    self.bbox_bottom_np_ = self.rigid_body_np_.attachNewNode(
      self.__createBulletGhostNodeFromBoxes__([bottom], scale,self.getName() + '-actor-bbbottom-gn'))
    self.bbox_back_np_ = self.rigid_body_np_.attachNewNode(
      self.__createBulletGhostNodeFromBoxes__([left], scale, self.getName() + '-actor-bbback-gn'))
    self.bbox_front_np_ = self.rigid_body_np_.attachNewNode(
      self.__createBulletGhostNodeFromBoxes__([right], scale, self.getName() + '-actor-bbfront-gn'))    
    
    self.bbox_top_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_TOP)
    self.bbox_bottom_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_BOTTOM)
    self.bbox_back_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_LEFT)
    self.bbox_front_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_RIGHT)
    
  
  def __createBulletGhostNodeFromBoxes__(self,boxes,scale, name ):
        
    ghost_node = BulletGhostNode(name)    
    transform  = TransformState.makeIdentity()      
    
    for box in boxes:
      box.scale = scale
      size = box.size
      center = box.center
      box_shape = BulletBoxShape(Vec3(0.5*size[0],0.5*AnimationActor.DEFAULT_WIDTH,0.5 * size[1]))
      #box_shape.setMargin(AnimationActor.COLLISION_MARGIN)
      transform = transform.setPos(Vec3(center[0],0,center[1]))
      ghost_node.addShape(box_shape,transform)
      
    return ghost_node
      
  
  def __createAnimationSequence__(self,name,sprite_images,sprites_time,is_left = False):
    """
      Creates the sequence node that plays these images
    """
    
    seq = SpriteSequencePlayer(name)
    
    for i in range(0,len(sprite_images)):
        
      txtr = sprite_images[i]
      
      w = txtr.getXSize() 
      h = txtr.getYSize()       
      
      # creating CardMaker to hold the texture
      cm = CardMaker(name +    str(i))
      cm.setFrame(0,w,-h,0 )  # This configuration places the image's topleft corner at the origin
      card = NodePath(cm.generate())            
      card.setTexture(txtr)
      seq.addChild(card.node(),i)
      seq.addFrame(card.node(),i,sprites_time[i])
      
      # offseting image
      xoffset = float(txtr.axisx + (-w if is_left else 0))
      yoffset = float(txtr.axisy)
      card.setPos(Vec3(xoffset,0,yoffset))
      
      AnimationActor.LOGGER.debug("Animation %s Sprite [%i] image size %s and offset %s."%( name,i, str((w,h)), str((txtr.axisx,txtr.axisy)) ) ) 
     
               
    return seq     
    
    
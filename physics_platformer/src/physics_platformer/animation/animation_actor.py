from physics_platformer.sprite import Sprite
from physics_platformer.sprite import SpriteGroup
from physics_platformer.sprite import SpriteAnimator
from physics_platformer.animation import AnimationInfo
from physics_platformer.collision import *
from physics_platformer.geometry2d import Box2D
from panda3d.core import NodePath, BoundingVolume
from panda3d.bullet import BulletRigidBodyNode
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


class AnimationActor(SpriteAnimator):
  
  DEFAULT_WIDTH = 0.001
  DEFAULT_MASS = 1.0
  BOUND_PADDING = 0.1
  
  def __init__(self,name,mass = DEFAULT_MASS):
    SpriteAnimator.__init__(self,name)
    
    self.mass_ = mass
    self.animation_action_ = None
    self.rigid_body_np_ = None # NodePath to a bullet rigid body that contains the collision boxes that are used to handle interactions with the environment    
    self.action_body_np_ = None # NodePath to a bullet ghost node containing boxes that will be used to trigger a specific player action upon coming into contact with the environment
    self.damage_box_np_ = None # NodePath to a bullet ghost node containing collision boxes that are active during the duration of the animation
    self.hit_box_np_ = None # NodePath to a bullet ghost node containing hit boxes that are active during the duration of the animation
    self.parent_physics_world_ = None
    
    # bounds    
    self.rigid_body_bbox_ = None
    self.bbox_top_np_ = None  # Node path to the top box ghost node
    self.bbox_bottom_np_ = None # Node path to the bottom box ghost node
    self.bbox_left_np_ = None # Node path to the left box ghost node
    self.bbox_right_np_ = None # Node path to the right box ghost node    
   
    self.node().setPythonTag(SpriteAnimator.__name__,self)
    
  def setPythonTag(self,tag,obj):
    SpriteAnimator.setPythonTag(self,tag,obj)       
    for np in [self.rigid_body_np_,self.damage_box_np_,self.hit_box_np_,self.action_body_np_,
               self.bbox_top_np_, self.bbox_right_np_, self.bbox_bottom_np_,self.bbox_left_np_]:
      if np is not None:
        np.setPythonTag(tag,obj)
    
  def loadAnimation(self,animation):
    """
    Loads the animation data from a AnimationInfo object
    """    
    if type(animation) is not AnimationInfo:
      logging.error("Object pass is not an instance of the AnimationInfo class")
      return False
    
    # load sprites
    if not self.loadAnimationSprites(animation.sprites_right, animation.sprites_left, animation.framerate):
      logging.error('Failed to load sprites from AnimationInfo object')
      return False
    
    # scale    
    scale = (animation.scalex, animation.scaley)
    
    # saving animation
    self.animation_action_ = animation
    
    # creating representative rigid body (Used to determine collisions with the environment
    self.__createRigidBody__(scale)
    
    # creating bullet ghost body for detecting interactions with the environment
    if len(self.animation_action_.action_boxes) > 0: # collecting boxes from each individual sprite          
      self.action_body_np_ =  self.rigid_body_np_.attachNewNode( self.__createBulletGhostNodeFromBoxes__(self.animation_action_.action_boxes,scale) )
      self.action_body_np_.node().setIntoCollideMask(CollisionMasks.ACTION_BODY)

    # creating attack collision and hit ghosts bodies for detecting oponent's attacks
    col_boxes = []    
    hit_boxes = []
    for elmt in self.animation_action_.animation_elements:
      col_boxes = col_boxes + elmt.damage_boxes
      hit_boxes = hit_boxes + elmt.hit_boxes
      
    if len(col_boxes) > 0:  
      col_boxes = [Box2D.createBoundingBox(col_boxes)]            
      self.damage_box_np_ = self.rigid_body_np_.attachNewNode( self.__createBulletGhostNodeFromBoxes__(col_boxes,scale) )
      self.damage_box_np_.node().setIntoCollideMask(CollisionMasks.ATTACK_DAMAGE)
      
    if len(hit_boxes) > 0:
      hit_boxes = [Box2D.createBoundingBox(hit_boxes)]
      self.hit_box_np_ = self.rigid_body_np_.attachNewNode( self.__createBulletGhostNodeFromBoxes__(hit_boxes,scale))
      self.hit_box_np_.node().setIntoCollideMask(CollisionMasks.ATTACK_HIT)
      
    self.setScale(Vec3(scale[0],1,scale[1]))
          
    return True
    
  def activate(self,physics_world,parent_np):    
    
    self.parent_physics_world_ = physics_world
    if self.rigid_body_np_ is not None:
      self.rigid_body_np_.reparentTo(parent_np)  
      for np in [self.bbox_top_np_, self.bbox_right_np_, self.bbox_bottom_np_,self.bbox_left_np_]:
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
      for np in [self.bbox_top_np_, self.bbox_right_np_, self.bbox_bottom_np_,self.bbox_left_np_]:
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
    return (None if (self.action_body_np_ is None) else self.action_body_np_)
    
  def loadAnimationSprites(self,sprites_right, sprites_left,framerate):
    """
    loadAnimationSprites
      Loads Sprites for the right and left animations
      Inputs:
      - sprites_right: list[Sprite] list of images for the right side
      - sprites_left: list[Sprite] list of images for the left side
      - framerate: (double) 
      - scale: (Vec3) Only the x and z values are used 
    """
    
    if (len(sprites_right) == 0) or (len(sprites_left) == 0):
      logging.error("ERROR: Found empty image list")
      return False
    
    if len(sprites_right) != len(sprites_left):
      logging.error("Unequal number of images for the left and right side")
      return False
    
    # storing individual sprite size
    w = sprites_right[0].getXSize() # assumes that all images in the in 'images' array are the same size
    h = sprites_right[0].getYSize()
    self.size_ = (w,h) # image size in pixels
    
    self.seq_right_ = self.__createAnimationSequence__(str(self.getName() )+ '-right-seq',sprites_right,framerate,False)
    self.seq_left_ = self.__createAnimationSequence__(str(self.getName() ) + '-left-seq',sprites_left,framerate,True)
    self.node().addStashed(self.seq_right_)
    self.node().addStashed(self.seq_left_)
    
    self.faceRight(True)     
    
    return True
  
  def setScale(self,scale):
    """
    Sets the scale of the animated sprites, collision and hit boxes in the actor
    """
    SpriteAnimator.setScale(self,Vec3(scale.getX(),1,scale.getZ()))
    
    if self.animation_action_ is None:
      return  
    
    # scaling sprite boxes
    for i in range(0,len(self.animation_action_.sprites_left)):      
      sprt_right = self.animation_action_.sprites_right[i]
      sprt_left = self.animation_action_.sprites_left[i]      
      boxes = sprt_right.hit_boxes + sprt_right.damage_boxes + sprt_left.hit_boxes + sprt_left.damage_boxes
      for box in boxes:
        box.scale = (scale.getX(), scale.getZ())
     
    
  def __createRigidBody__(self,scale):
    self.rigid_body_np_ = NodePath(BulletRigidBodyNode('RigidBody'))
    rigid_body = self.rigid_body_np_.node()
    rigid_body.setIntoCollideMask(CollisionMasks.RIGID_BODY)
    rigid_body.setDeactivationEnabled(False,True)
    
    # collection all boxes
    collision_boxes = []
    if len(self.animation_action_.rigid_body_boxes) > 0:      
      # use existing collision boxes 
      collision_boxes = self.animation_action_.rigid_body_boxes
      logging.info("Using existing rigid body boxes: %s "%( ';'.join(str(x) for x in collision_boxes ) ))
    else:      
      # compute bounding box of all collision boxes from every sprite 
      boxes = []
      for elemt in self.animation_action_.animation_elements:
        boxes = boxes + elemt.damage_boxes
      
      if len(boxes) > 0:
        collision_boxes = [Box2D.createBoundingBox(boxes)]
        
      
    # create rigid body
    for box in collision_boxes:
      box.scale = scale
      size = box.size
      center = box.center
      transform = TransformState.makeIdentity()
      box_shape = BulletBoxShape(Vec3(0.5*size[0],0.5*AnimationActor.DEFAULT_WIDTH,0.5 * size[1]))
      transform = transform.setPos(Vec3(center[0],0,center[1]))
      rigid_body.addShape(box_shape,transform)
      
    # completing rigid body setup
    rigid_body.setMass(self.mass_)
    rigid_body.setLinearFactor((1,0,1))   
    rigid_body.setAngularFactor((0,0,0)) 
    rigid_body.setBoundsType(BoundingVolume.BT_box)
    
    # creating bounding box    
    self.rigid_body_bbox_ = Box2D.createBoundingBox(collision_boxes)
    
    # creating bounding boxes around rigid body
    top = Box2D(self.rigid_body_bbox_.width, AnimationActor.BOUND_PADDING ,(0, self.rigid_body_bbox_.height + 0.5*AnimationActor.BOUND_PADDING))
    bottom = Box2D(self.rigid_body_bbox_.width, AnimationActor.BOUND_PADDING ,(0, -0.5*AnimationActor.BOUND_PADDING))
    left = Box2D(AnimationActor.BOUND_PADDING, self.rigid_body_bbox_.height,( -0.5*(self.rigid_body_bbox_.width + AnimationActor.BOUND_PADDING), 0.5*self.rigid_body_bbox_.height))
    right = Box2D(AnimationActor.BOUND_PADDING, self.rigid_body_bbox_.height ,( 0.5*(self.rigid_body_bbox_.width + AnimationActor.BOUND_PADDING), 0.5*self.rigid_body_bbox_.height))
    
    scale = (1,1)
    self.bbox_top_np_ = self.rigid_body_np_.attachNewNode(self.__createBulletGhostNodeFromBoxes__([top], scale))
    self.bbox_bottom_np_ = self.rigid_body_np_.attachNewNode(self.__createBulletGhostNodeFromBoxes__([bottom], scale))
    self.bbox_left_np_ = self.rigid_body_np_.attachNewNode(self.__createBulletGhostNodeFromBoxes__([left], scale))
    self.bbox_right_np_ = self.rigid_body_np_.attachNewNode(self.__createBulletGhostNodeFromBoxes__([right], scale))    
    
    self.bbox_top_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_TOP)
    self.bbox_bottom_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_BOTTOM)
    self.bbox_left_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_LEFT)
    self.bbox_right_np_.node().setIntoCollideMask(CollisionMasks.GAME_OBJECT_RIGHT)
    
  
  def __createBulletGhostNodeFromBoxes__(self,boxes,scale ):
        
    ghost_node = BulletGhostNode("HitBody")    
    transform  = TransformState.makeIdentity()      
    
    for box in boxes:
      box.scale = scale
      size = box.size
      center = box.center
      box_shape = BulletBoxShape(Vec3(0.5*size[0],0.5*AnimationActor.DEFAULT_WIDTH,0.5 * size[1]))
      transform = transform.setPos(Vec3(center[0],0,center[1]))
      ghost_node.addShape(box_shape,transform)
      
    return ghost_node
      
  
  def __createAnimationSequence__(self,name,sff_images,framerate,is_left = False):
    """
      Creates the sequence node that plays these images
    """
    seq = SequenceNode(name)
    
    for i in range(0,len(sff_images)):
        
      txtr = sff_images[i]
      
      w = txtr.getXSize() 
      h = txtr.getYSize()       
      
      # creating CardMaker to hold the texture
      cm = CardMaker(name +    str(i))
      cm.setFrame(0,w,-h,0 )  # This configuration places the image's topleft corner at the origin
      #cm.setFrame(-0.5*w,0.5*w,-h,0)  
      card = NodePath(cm.generate())            
      card.setTexture(txtr)
      seq.addChild(card.node(),i)
      
      # offseting image
      xoffset = float(txtr.axisx + (-w if is_left else 0))
      yoffset = float(txtr.axisy)
      card.setPos(Vec3(xoffset,0,yoffset))
      
      logging.debug("Animation %s Sprite [%i] image size %s and offset %s."%( name,i, str((w,h)), str((txtr.axisx,txtr.axisy)) ) ) 
     
    seq.setFrameRate(framerate)            
    return seq     
    
    
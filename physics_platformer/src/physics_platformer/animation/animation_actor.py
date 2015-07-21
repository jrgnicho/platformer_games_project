from physics_platformer.sprite import Sprite
from physics_platformer.sprite import SpriteGroup
from physics_platformer.sprite import SpriteAnimator
from physics_platformer.animation import AnimationAction
from panda3d.core import NodePath
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletGhostNode
from panda3d.bullet import BulletBoxShape
from panda3d.core import TransformState
from panda3d.core import SequenceNode
from panda3d.core import Texture
from panda3d.core import Vec3
import logging
from panda3d.bullet import BulletRigidBodyNode


class AnimationActor(SpriteAnimator):
  
  __DEFAULT_WIDTH__ = 0.01
  __DEFAULT_MASS__ = 0.01
  
  def __init__(self,name):
    SpriteAnimator.__init__(self,name)
    
    self.animation_action_ = None
    self.rigid_body_np_ = None # NodePath to a bullet rigid body that contains the collision boxes
    self.collision_body_np_ = None # NodePath to a bullet ghost node containing collision boxes that are active during the duration of the animation
    self.action_body_np_ = None # NodePath to a bullet ghost node containing boxes that will be used to trigger a specific player action
    self.constraint_joint_ = None # bullet constraints that connects the collision body to its parent
    
    
  def loadAnimation(self,animation):
    """
    Loads the animation data from a AnimationAction object
    """    
    if type(animation) is not AnimationAction:
      logging.error("Object pass is not an instance of the AnimationAction class")
      return False
    
    # load sprites
    if not self.loadAnimationSprites(animation.sprites_right, animation.sprites_right, animation.framerate):
      logging.error('Failed to load sprites from AnimationAction object')
      return False
    
    # saving animation
    self.animation_action_ = animation
    
    # creating representative rigid body (Used to determine collisions with the environment
    self.__createRigidBody__()
    
    # creating hit body for detecting when player's attacks landed
    action_boxes = self.animation_action_.action_boxes
    if len(self.animation_action_.action_boxes) == 0: # collecting boxes from each individual sprite
      for elmt in self.animation_action_.animation_elements:
        action_boxes = action_boxes + elmt.hit_boxes
    
      # creating bounding box from all boxes
      action_boxes = [Box2D.union(action_boxes)]     
      
    self.action_body_np_ =  self.rigid_body_np_.attachNewNode( self.__createBulletGhostNodeFromBoxes__(action_boxes) )
        
    # creating collision body for detecting oponent's attacks
    col_boxes = []
    if len(col_boxes) == 0:
      for elmt in self.animation_action_.animation_elements:
        col_boxes = col_boxes + elmt.collision_boxes
        
      col_boxes = [Box2D.union(col_boxes)]
            
    self.collision_body_np_ = self.rigid_body_np_.attachNewNode( self.__createBulletGhostNodeFromBoxes__(col_boxes) )
    
    
    return True
    
    
    
  def getCollisionGhostBody(self):
    """
    Returns ghost body used to determing in an opponent's attack reached the player
    """
    return self.collision_body_np_.node()
  
  def getActionGhostBody(self):
    """
    Returns ghost body for determining that the action geometry is in overlap
    """
    return self.action_body_np_.node()
    
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
    
    self.seq_right_ = self.__createAnimationSequence__(self.getName() + '-right-seq',sprites_right,frame_rate)
    self.seq_left_ = self.__createAnimationSequence__(self.getName()+ '-left-seq',sprites_left,frame_rate)
    self.node().addStashed(self.seq_right_)
    self.node().addStashed(self.seq_left_)
    
    self.faceRight(True)     
    
    return True
  
  def setScale(self,scale):
    """
    Sets the scale of the animated sprites, collision and hit boxes in the actor
    """
    SpriteAnimator.setScale(self,Vec3(scale.getX(),1,scale.getZ()))
    self.rigid_body_np_.setScale(Vec3(scale.getX(),1,scale.getZ()))
    
    # scaling sprite boxes
    for i in range(0,self.animation_action_.sprites_left):      
      sprt_right = self.animation_action_.sprites_right[i]
      sprt_left = self.animation_action_.sprites_left[i]      
      boxes = sprt_right.hit_boxes + sprt_right.collision_boxes + sprt_left.hit_boxes + sprt_left.collision_boxes
      for box in boxes:
        box.scale((scale.getX(), scale.getZ()))
    
    
    
  def __createRigidBody__(self):
    self.rigid_body_np_ = NodePath(BulletRigidBodyNode('RigidBody'))
    rigid_body = self.rigid_body_np_.node()
    
    # collection all boxes
    collision_boxes = []
    if len(self.animation_action.rigid_body_boxes) > 0:      
      # use existing collision boxes 
      collision_boxes = self.animation_action.rigid_body_boxes
    else:      
      # compute bounding box of all collision boxes from every sprite 
      boxes = []
      for elemt in self.animation_action_.animation_elements:
        boxes = boxes + elemt.collision_boxes
        
      collision_boxes = [Box2D.createBoundingBox(boxes)]
      
    # create rigid body
    for box in collision_boxes:
      size = box.size
      center = box.center
      transform = TransformState.makeIdentity()
      box_shape = BulletBoxShape(0.5*size[0],0.5*AnimationActor.__DEFAULT_WIDTH__,0.5 * size[1])
      transform = transform.setPos(Vec3(center[0],0,center[1]))
      rigid_body.addShape(box_shape,transform)
      
    # completing rigid body setup
    rigid_body.setMass(AnimationAction.__DEFAULT_MASS__)
    rigid_body.setLinearFactor((1,0,1))   
    rigid_body.setAngularFactor((0,1,0))   
    rigid_body.setIntoCollideMask(BitMask32().allOn())
    
  
  def __createBulletGhostNodeFromBoxes__(self,boxes):
        
    ghost_node = BulletGhostNode("HitBody")    
    transform  = TransformState.makeIdentity()      
    
    for box in boxes:
      size = box.size
      center = box.center
      box_shape = BulletBoxShape(0.5*size[0],0.5*AnimationActor.__DEFAULT_WIDTH__,0.5 * size[1])
      transform = transform.setPos(Vec3(center[0],0,center[1]))
      ghost_node.addShape(box_shape,transform)
      
    return ghost_node
      
  
  def __createAnimationSequence__(self,name,sff_images,framerate):
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
        cm.setFrame(0,w,-h,0)  # This configuration places the image's topleft corner at the origin
        card = NodePath(cm.generate())            
        card.setTexture(txtr)
        seq.addChild(card.node(),i)
        
        # offseting image
        card.setPos(Vec3(txtr.axisx,0,txtr.axisy))
     
    seq.setFrameRate(framerate)           
    print "Sequence Node %s contains %i imagese of size %s and card size of %s"%(name,seq.getNumFrames(),str((w,h)),str((cw,ch)))        
    return seq     
    
    
from panda3d.core import Vec3

class CharacterInfo(object):
  
  def __init__(self):
    self.width = 0.4
    self.height = 0.6
    self.name = 'Ramapithecus'
    self.mass = 1
    self.scale = Vec3(1,1,1)
    self.life = 100
    self.power = 100
    self.attack = 100
    self.defense = 100
    self.air_jumps = 1
    self.walk_speed = 1
    self.run_speed = 2
    self.jump_force = 1
    self.jump_forward = 1
    
  def __str__(self):
    
    s = """
    Character Info:
      name:   %s
      mass:   %f
      height: %f
      width:  %f
      scale:  (%f, %f)
      life:   %i
      power:  %i
      attack: %i
      defense: %i
      air_jumps:  %i
      walk_speed:  %f
      run_speed:  %f
      jump_force:  %f
      jump_forward:  %f
    """%(self.name,
         self.mass,
         self.height,
         self.width,
         self.scale.getX(),self.scale.getZ(),
         self.life,
         self.power,
         self.attack,
         self.defense,
         self.air_jumps,
         self.walk_speed,
         self.run_speed,
         self.jump_force,
         self.jump_forward)
    return s
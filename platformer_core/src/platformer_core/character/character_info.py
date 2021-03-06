from panda3d.core import Vec3

class CharacterInfo(object):
  
  def __init__(self):
    self.width = 0.4
    self.height = 0.6
    self.name = 'Ramapithecus'
    self.mass = 2.0
    self.friction = 0.2
    self.scale = Vec3(1,1,1)
    self.life = 100
    self.power = 100
    self.attack = 100
    self.defense = 100
    self.air_jumps = 1
    self.air_dashes = 1
    self.walk_speed = 1
    self.run_speed = 2
    self.dash_speed = 4
    self.jump_force = 1
    self.airjump_force = 1
    self.jump_fwd_speed = 1
    self.jump_momentum = 0.6 # percentage of the forward momemtum retained during jumping
    self.fall_max_speed = -8
    self.fall_recovery_min = 0.2 # minimum distance from edge for attempting a recovery and avoid falling from edge,
                                 # when less than this value the character is pushed out of the platform
    self.fall_recovery_max = 0.5 # at this distance from the edge then the character performs a normal land action
    self.land_edge_min = 0.1
    self.land_edge_max = 0.6
    
  def __str__(self):
    
    s = """
    Character Info:
      name:   %s
      mass:   %f
      friction: %f
      height: %f
      width:  %f
      scale:  (%f, %f)
      life:   %i
      power:  %i
      attack: %i
      defense: %i
      air_jumps:  %i
      air_dashes: %i
      walk_speed:  %f
      run_speed:  %f
      dash_speed: %f
      jump_force:  %f
      airjump_force: %f
      jump_fwd_speed:  %f
      jump_momentum: %f
      fall_max_speed:  %f
      fall_recovery_min: %f
      fall_recovery_max: %f
      land_edge_min: %f
      land_edge_max: %f
    """%(self.name,
         self.mass,
         self.friction,
         self.height,
         self.width,
         self.scale.getX(),self.scale.getZ(),
         self.life,
         self.power,
         self.attack,
         self.defense,
         self.air_jumps,
         self.air_dashes,
         self.walk_speed,
         self.run_speed,
         self.dash_speed,
         self.jump_force,
         self.airjump_force,
         self.jump_fwd_speed,
         self.jump_momentum,
         self.fall_max_speed,
         self.fall_recovery_min,
         self.fall_recovery_max,
         self.land_edge_min,
         self.land_edge_max)
    return s
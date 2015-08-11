from panda3d.core import Vec3

class CharacterInfo(object):
  
  def __init__(self):
    self.name = 'Ramapithecus'
    self.mass = 1
    self.scale = Vec3(1,1,1)
    self.life = 100
    self.power = 100
    self.attach = 100
    self.defense = 100
    self.air_jumps = 1
    self.walk_speed = 1
    self.run_speed = 2
    self.jump_force = 1
    self.jump_forward = 1
from combat_platformer.player import PlayerBase
from combat_platformer.enemy import EnemyProperties

class EnemyBase(PlayerBase):
    
    def __init__(self):
        PlayerBase.__init__(self)
        self.properties = EnemyProperties()
        
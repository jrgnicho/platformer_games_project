from physics_platformer.state_machine import Action

class GeneralActions(object):    
  
  GAME_STEP = "GAME_STEP"
  
  class GameStep(Action):
    def __init__(self,dt):
      Action.__init__(self,GeneralActions.GAME_STEP)
      self.dt = dt
    

  
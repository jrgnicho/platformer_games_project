#!/usr/bin/env python
import pygame
from combat_platformer.input import JoystickButtons
from combat_platformer.input import Move
from combat_platformer.input import JoystickManager

class TestJoystickManager:
    
    def __init__(self):
        
        # Creating button map
        button_map = {0 : JoystickButtons.BUTTON_X , 3 : JoystickButtons.BUTTON_Y,
                      1 : JoystickButtons.BUTTON_A , 2 : JoystickButtons.BUTTON_B,
                      7 : JoystickButtons.TRIGGER_R1 , 5 : JoystickButtons.TRIGGER_R2,
                      6 : JoystickButtons.TRIGGER_L1 , 4 : JoystickButtons.TRIGGER_L2,
                      9 : JoystickButtons.BUTTON_START , 8 : JoystickButtons.BUTTON_SELECT}
        
        
        self.joystick_manager = JoystickManager(button_map,JoystickManager.JoystickAxes(),1000 )
        
        # Creating directional moves
        self.joystick_manager.add_move(Move('UP',[JoystickButtons.DPAD_UP],True))
        self.joystick_manager.add_move(Move('DOWN',[JoystickButtons.DPAD_DOWN],True))
        self.joystick_manager.add_move(Move('LEFT',[JoystickButtons.DPAD_LEFT],True))
        self.joystick_manager.add_move(Move('RIGHT',[JoystickButtons.DPAD_RIGHT],True))
        self.joystick_manager.add_move(Move('DOWN_RIGHT',[JoystickButtons.DPAD_DOWNRIGHT],True))
        self.joystick_manager.add_move(Move('UP_LEFT',[JoystickButtons.DPAD_UPLEFT],True))
        
        # Creating action moves
        self.joystick_manager.add_move(Move('JUMP',[JoystickButtons.BUTTON_B],True))
        self.joystick_manager.add_move(Move('DASH',[JoystickButtons.BUTTON_A],True))
        self.joystick_manager.add_move(Move('LIGHT ATTACK',[JoystickButtons.BUTTON_Y],True))
        self.joystick_manager.add_move(Move('FUERTE ATTACK',[JoystickButtons.BUTTON_X],True))
        
        # Creating special moves
        self.joystick_manager.add_move(Move('ABUKE',[JoystickButtons.DPAD_DOWN,
                                                     JoystickButtons.DPAD_DOWNRIGHT,
                                                     JoystickButtons.DPAD_RIGHT,
                                                     JoystickButtons.DPAD_RIGHT | JoystickButtons.BUTTON_Y],False))
    
    def run(self):
        
        proceed = True
        clock = pygame.time.Clock()
        
        
        while proceed:
            
            self.joystick_manager.update(clock.get_time())
            
            pygame.display.flip()
            clock.tick(20)
                       
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    proceed = False
        
        
        
        
        
        
if __name__ == "__main__":
    
    # initialize pygame
    pygame.init()
    size = [500, 700]
    screen = pygame.display.set_mode(size)
    screen.fill((255,255,255))
    pygame.display.set_caption("JoystickManager Test")
    
    # Initializing joystick support
    pygame.joystick.init()
    
    test = TestJoystickManager()
    test.run()    
    
    pygame.quit ()
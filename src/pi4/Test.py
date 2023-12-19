import os
import pygame
import time
# pylint: disable=all
os.environ['XDG_RUNTIME_DIR'] = '/run/user/1000'
os.environ["DISPLAY"] = ":0"
class pyscope:
    screen = None
    def __init__(self):
        self.screen = pygame.display.set_mode((100, 100), pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def test(self):
        # Fill the screen with red (255, 0, 0)
        red = (255, 0, 0)
        self.screen.fill(red)
        # Update the display
        pygame.display.update()

# Create an instance of the PyScope class
scope = pyscope()
scope.test()
time.sleep(5)
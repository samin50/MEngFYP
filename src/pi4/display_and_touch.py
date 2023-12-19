"""
Code for handing 7 inch DFROBOT display and touch screen
"""
import pygame
import os
os.environ["SDL_FBDEV"] = "/dev/fb0"
# pylint: disable=no-member
class Display():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()

    def draw_text(self, textStr:str):
        """
        Draw text on the display
        """
        while True:
            self.screen.fill((255, 255, 255))
            font = pygame.font.Font(None, 50)
            text = font.render(textStr, True, (255, 0, 0))
            self.screen.blit(text, (0, 0))
        print(textStr)

# Test code for display
if __name__ == "__main__":
    display = Display()
    display.draw_text("Display Test")

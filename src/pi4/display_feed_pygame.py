"""
Pygame implementation of the display feed.
Done to hopefully improve performance
Also uses threading to improve performance
"""
import pygame
from src.common.constants import CAMERA_RESOLUTION, FPS_FONT_SIZE, CAMERA_FRAMERATE
from src.common.helper_functions import start_ui
from src.pi4.vision_handler import Vision_Handler
class CameraFeed:
    def __init__(self, size:tuple, cameraDisplay:pygame.display, visionHandler:Vision_Handler, trainingMode:bool=False) -> None:
        self.cameraDisplay = cameraDisplay
        self.size = size
        self.trainingMode = trainingMode
        self.currentFrame = pygame.Surface(CAMERA_RESOLUTION)
        self.resizedFrame = pygame.Surface(self.size)
        self.vision = visionHandler
        # FPS
        self.fpsFont = pygame.font.SysFont("Roboto", FPS_FONT_SIZE)
        self.fps = self.fpsFont.render("FPS: 0", True, (255,255,255))
        self.cameraclock = pygame.time.Clock()
        self.drawFPSEvent = pygame.USEREVENT + 100
        pygame.time.set_timer(self.drawFPSEvent, 1000 // CAMERA_FRAMERATE)

    def update_frame(self) -> pygame.Surface:
        """
        Obtain the current frame from the camera, if available
        """
        _ = self.cameraclock.tick(CAMERA_FRAMERATE) / 1000.0
        self.currentFrame = self.vision.get_frame()
        # Draw FPS in the bottom right corner
        if not self.trainingMode:
            self.resizedFrame = pygame.transform.scale(self.currentFrame, self.size)
            self.resizedFrame.blit(self.fps, (self.size[0]-(self.fps.get_width()+5), self.size[1]-(self.fps.get_height())))
        else:
            padding = 10
            self.resizedFrame = pygame.transform.scale(self.currentFrame, (self.size[0]-padding, self.size[1]-padding))
            backgroundFrame = pygame.Surface(self.size)
            backgroundFrame.fill((255, 0, 255))
            backgroundFrame.blit(self.resizedFrame, (padding//2, padding//2))
            self.resizedFrame = backgroundFrame
        # Draw the frame
        self.cameraDisplay.blit(self.resizedFrame, (0,0))
        return self.currentFrame

    def event_handler(self, event:pygame.event.Event) -> None:
        """
        Handle pygame events
        """
        if event.type == self.drawFPSEvent:
            self.update_frame()
            self.fps = self.fpsFont.render(f"FPS: {self.cameraclock.get_fps():.0f}", True, (255,255,255))

if __name__ == '__main__':
    TRAINING_MODE = False
    pygame.init()
    clk = pygame.time.Clock()
    display = pygame.display.set_mode(CAMERA_RESOLUTION, 0)
    camera = CameraFeed(CAMERA_RESOLUTION, display, TRAINING_MODE)
    start_ui(
        loopConditionFunc=lambda: True,
        loopFunction=[],
        eventFunction=[camera.event_handler],
        exitFunction=[camera.vision.destroy],
        clock=clk,
        )

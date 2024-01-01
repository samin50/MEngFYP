"""
Pygame implementation of the display feed.
Done to hopefully improve performance
Also uses threading to improve performance
"""
import threading
import time
import pygame
import pygame.camera as pycam
from src.common.constants import CAMERA_RESOLUTION, FPS_FONT_SIZE, CAMERA_FRAMERATE
from src.common.helper_functions import start_ui

class CameraFeed:
    def __init__(self, size:tuple, clock:pygame.time.Clock, cameraDisplay:pygame.display) -> None:
        self.cameraDisplay = cameraDisplay
        self.size = size
        self.currentFrame = pygame.Surface(CAMERA_RESOLUTION)
        self.resizedFrame = pygame.Surface(self.size)
        # FPS
        self.fpsFont = pygame.font.SysFont("Roboto", FPS_FONT_SIZE)
        self.fps = self.fpsFont.render("FPS: 0", True, (255,255,255))
        self.clock = clock
        self.framePeriod = float(1) / CAMERA_FRAMERATE
        # Grab the available camera and start it
        pycam.init()
        self.camlist = pycam.list_cameras()
        self.cam = pycam.Camera(self.camlist[0])
        self.stopThread = False
        self.frameThread = threading.Thread(target=self.run, daemon=True)
        self.frameThread.start()

    def run(self) -> None:
        """
        Run threaded camera loop
        """
        self.cam.start()
        while not self.stopThread:
            self.update_frame()
            time.sleep(self.framePeriod)

    def update_frame(self) -> pygame.Surface:
        """
        Obtain the current frame from the camera, if available
        """
        if self.cam.query_image():
            self.currentFrame = self.cam.get_image(self.currentFrame)
        self.resizedFrame = pygame.transform.scale(self.currentFrame, self.size)
        # Draw FPS in the bottom right corner
        self.fps = self.fpsFont.render(f"FPS: {self.clock.get_fps():.0f}", True, (255,255,255))
        self.resizedFrame.blit(self.fps, (self.size[0]-(self.fps.get_width()+5), self.size[1]-(self.fps.get_height())))
        # Draw the frame
        self.cameraDisplay.blit(self.resizedFrame, (0,0))
        return self.currentFrame

    def destroy(self):
        """
        Stop the thread and release the camera.
        """
        self.stopThread = True
        self.frameThread.join()
        self.cam.stop()

if __name__ == '__main__':
    pygame.init()
    clk = pygame.time.Clock()
    display = pygame.display.set_mode(CAMERA_RESOLUTION, 0)
    camera = CameraFeed(CAMERA_RESOLUTION, clk, display)
    start_ui([], [camera.destroy], clock=clk)

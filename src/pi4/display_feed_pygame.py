"""
Pygame implementation of the display feed.
Done to hopefully improve performance
Also uses threading to improve performance
"""
import pygame
import pygame.camera as pycam
from src.common.constants import CAMERA_RESOLUTION, CAMERA_FRAMERATE
from src.common.helper_functions import start_ui
from src.common.simulate import FakeCamera
class CameraFeed:
    def __init__(self, cameraDisplay:pygame.display, trainingMode:bool=False) -> None:
        self.cameraDisplay = cameraDisplay
        self.trainingMode = trainingMode
        self.currentFrame = pygame.Surface(CAMERA_RESOLUTION)
        # Camera setup
        self.realCamera = None
        self.fakeCamera = FakeCamera(0)
        self.cameraclock = pygame.time.Clock()
        pycam.init()

    def set_camera(self) -> None:
        """
        Set the camera if it becomes unavailable
        """
        camList = pycam.list_cameras()
        if len(camList) != 0:
            try:
                # Important for performance to stop the camera before starting it again
                if self.realCamera is not None:
                    self.realCamera.stop()
                self.realCamera = pycam.Camera(camList[0])
                self.realCamera.start()
            except:
                self.realCamera = None
        return

    def get_frame(self) -> pygame.Surface:
        """
        Get the current frame from the camera
        """
        try:
            self.currentFrame = self.realCamera.get_image(self.currentFrame)
        except:
            self.currentFrame = self.fakeCamera.get_image(self.currentFrame)
            self.set_camera()
        return self.currentFrame

    def update_frame(self) -> None:
        """
        Display camera, but only used if this file is run directly
        """
        _ = self.cameraclock.tick(CAMERA_FRAMERATE) / 1000.0
        self.currentFrame = self.get_frame()
        # Draw the frame
        self.cameraDisplay.blit(self.currentFrame, (0,0))

if __name__ == '__main__':
    TRAINING_MODE = False
    CAMERA_FRAMERATE = 30
    pygame.init()
    clk = pygame.time.Clock()
    display = pygame.display.set_mode(CAMERA_RESOLUTION, 0)
    camera = CameraFeed(display, TRAINING_MODE)
    start_ui(
        loopConditionFunc=lambda: True,
        loopFunction=[camera.update_frame],
        eventFunction=[],
        exitFunction=[],
        clock=clk,
        )

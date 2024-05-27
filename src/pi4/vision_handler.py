"""
Responsible for handling the vision system.
Hooks onto the pygame camera and performs inference.
"""
import pygame
import pygame.camera as pycam
from src.common.simulate import FakeCamera
from src.common.constants import CAMERA_RESOLUTION
class Vision_Handler:
    def __init__(self, enableInference:bool=False) -> None:
        self.enableInference = enableInference
        self.currentFrame = pygame.Surface(CAMERA_RESOLUTION)
        # Camera setup
        self.fakeCamera = FakeCamera(0)
        self.realCamera = None
        pycam.init()

    def set_camera(self) -> None:
        """
        Set the camera if it becomes unavailable
        """
        camList = pycam.list_cameras()
        if len(camList) != 0:
            if self.realCamera is None:
                self.realCamera = pycam.Camera(camList[0])
            try:
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
            # Try reconnecting the camera
            self.set_camera()
        return self.currentFrame

    def inference(self) -> None:
        """
        Perform inference on the current frame
        """
        frame = self.get_frame()
        if not self.enableInference:
            return frame

    def destroy(self) -> None:
        """
        Destroy the camera
        """
        if self.realCamera is not None:
            self.realCamera.stop()
        return

if __name__ == "__main__":
    pygame.init()
    vision = Vision_Handler()
    display = pygame.display.set_mode(CAMERA_RESOLUTION)
    while True:
        currentFrame = vision.inference()
        display.blit(currentFrame, (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                vision.destroy()
                pygame.quit()
                exit()

"""
Responsible for handling the vision system.
Hooks onto the pygame camera and performs inference.
"""
# pylint: disable=attribute-defined-outside-init
import multiprocessing
import numpy
import cv2
import pygame
import pygame.camera as pycam
import pyautogui
import pygetwindow
try:
    from ultralytics import YOLO
    print("Using ultralytics YOLO!")
except ImportError:
    from src.common.simulate import YOLO
    print("Using simulated YOLO!")
from src.pi4.display_feed_pygame import CameraFeed
from src.common.helper_functions import start_ui
from src.common.constants import CAMERA_RESOLUTION, CLASSIFIER_PATH, TRAINING_MODE_CAMERA_SIZE, CAMERA_DISPLAY_SIZE, FPS_FONT_SIZE, CAMERA_FRAMERATE
from src.vision.vsrc.constants import DATA, REALVNC_WINDOW_NAME, BORDER_WIDTH, LOWER_THRESHOLD, UPPER_THRESHOLD
class Vision_Handler:
    def init(self, cameraDisplay:pygame.display, componentDisplay:pygame.display, enableInference:bool=False, trainingMode:bool=False) -> None:
        """
        Initialise the vision handler
        """
        # Constants
        self.resolution = TRAINING_MODE_CAMERA_SIZE if trainingMode else CAMERA_DISPLAY_SIZE
        self.enableInference = enableInference
        self.trainingMode = trainingMode
        self.cameraDisplay = cameraDisplay
        self.componentDisplay = componentDisplay
        # Surface setup
        self.currentFrame = pygame.Surface(CAMERA_RESOLUTION)
        self.resizedFrame = pygame.Surface(self.resolution)
        # Inference and locks
        if self.enableInference:
            self.model = YOLO(CLASSIFIER_PATH)
        else:
            self.model = None
        self.labelFont = pygame.font.SysFont("Roboto", 20)
        # Camera setup
        self.cameraFeed = CameraFeed(self.cameraDisplay, trainingMode)
        # Class label font
        self.labelMap = {k["num_label"] : k["label"] for k in DATA.values()}
        # FPS
        self.fpsFont = pygame.font.SysFont("Roboto", FPS_FONT_SIZE)
        self.fps = self.fpsFont.render("FPS: 0", True, (255,255,255))
        self.cameraclock = pygame.time.Clock()
        self.drawFPSEvent = pygame.USEREVENT + 100
        pygame.time.set_timer(self.drawFPSEvent, 1000 // CAMERA_FRAMERATE)
        pycam.init()
        return self

    def update_frame(self) -> pygame.Surface:
        """
        Get the current frame from the camera
        """
        _ = self.cameraclock.tick(CAMERA_FRAMERATE) / 1000.0
        # Get the frame
        self.currentFrame = self.get_frame()
        # Resize the frame and draw FPS in the bottom right corner
        if not self.trainingMode:
            self.resizedFrame = pygame.transform.scale(self.currentFrame, self.resolution)
            self.resizedFrame.blit(self.fps, (self.resolution[0]-(self.fps.get_width()+5), self.resolution[1]-(self.fps.get_height())))
        else:
            padding = 10
            self.resizedFrame = pygame.transform.scale(self.currentFrame, (self.resolution[0]-padding, self.resolution[1]-padding))
            backgroundFrame = pygame.Surface(self.resolution)
            backgroundFrame.fill((255, 0, 255))
            backgroundFrame.blit(self.resizedFrame, (padding//2, padding//2))
            self.resizedFrame = backgroundFrame
        # Draw the frame
        self.cameraDisplay.blit(self.resizedFrame, (0,0))

    def event_handler(self, event:pygame.event.Event) -> None:
        """
        Handle pygame events
        """
        if event.type == self.drawFPSEvent:
            self.update_frame()
            self.fps = self.fpsFont.render(f"FPS: {self.cameraclock.get_fps():.0f}", True, (255,255,255))

    def get_frame(self) -> pygame.Surface:
        """
        Get the current frame
        """
        return self.cameraFeed.get_frame()

    def inference(self, frame:pygame.Surface) -> list:
        """
        Perform inference on the current frame
        """
        classList = []
        # Classifier
        imgData = pygame.surfarray.array3d(frame)
        results = self.model.predict(imgData, verbose=False)
        for result in results:
            clsList = result.obb.cls.tolist()
            # For every box
            for i, _ in enumerate(clsList):
                box = result.obb.xyxyxyxy[i].tolist()
                classList.append(clsList[i])
                conf = result.obb.conf[i].tolist()
                # Draw the bounding box
                pygame.draw.lines(frame, (255, 0, 0), True, box, 2)
                # Draw the class
                label = self.labelFont.render(f"{self.labelMap[clsList[i]]}:{conf:.2f}", True, (255, 0, 0))
                frame.blit(label, (box[0], box[1]))
        return frame

    def capture_vnc(self) -> None:
        """
        Capture an image from the Raspberry Pi.
        """
        # Focus on the RealVNC window
        try:
            realVNCWindow = pygetwindow.getWindowsWithTitle(REALVNC_WINDOW_NAME)[0]
            realVNCWindow.activate()
        except:
            return self.currentFrame
        # Capture the image
        screenshotPil = pyautogui.screenshot(region=(realVNCWindow.left, realVNCWindow.top, realVNCWindow.width, realVNCWindow.height))
        # Convert to OpenCV format
        screenshotCv = numpy.array(screenshotPil)
        # Find the contours defined by the pink square
        mask = cv2.inRange(cv2.cvtColor(screenshotCv, cv2.COLOR_BGR2HSV), LOWER_THRESHOLD, UPPER_THRESHOLD)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
        # Find the largest contour in the mask
            largestContour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largestContour)
            x, y, w, h = x+BORDER_WIDTH, y+BORDER_WIDTH, w-(BORDER_WIDTH*2), h-(BORDER_WIDTH*2)
            cameraRegion = screenshotCv[y:y+h, x:x+w]
            surface = pygame.surfarray.make_surface(cv2.cvtColor(cameraRegion, cv2.COLOR_BGR2RGB))
            surface = pygame.transform.flip(surface, True, False)
            surface = pygame.transform.rotate(surface, 90)
            return surface
        return self.currentFrame

    def destroy(self) -> None:
        """
        Destroy the camera
        """
        if self.realCamera is not None:
            self.realCamera.stop()
        return

if __name__ == "__main__":
    INFERENCE = True
    CAPTURE_VNC = False
    TRAINING_MODE = False
    pygame.init()
    clk = pygame.time.Clock()
    display = pygame.display.set_mode((CAMERA_RESOLUTION[0]//3+CAMERA_RESOLUTION[0], CAMERA_RESOLUTION[1]), 0)
    camera = pygame.Surface((CAMERA_RESOLUTION[0], CAMERA_RESOLUTION[1]))
    compDisplay = pygame.Surface((CAMERA_RESOLUTION[0]//3, CAMERA_RESOLUTION[1]))
    vision = Vision_Handler().init(camera, compDisplay, INFERENCE, TRAINING_MODE)
    start_ui(
        loopConditionFunc=lambda: True,
        loopFunction=[lambda: display.blit(camera, (0,0)), lambda: display.blit(compDisplay, (CAMERA_RESOLUTION[0], 0))],
        eventFunction=[vision.event_handler],
        exitFunction=[],
        clock=clk,
    )

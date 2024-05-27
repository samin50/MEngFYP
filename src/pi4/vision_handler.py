"""
Responsible for handling the vision system.
Hooks onto the pygame camera and performs inference.
"""
import numpy
import cv2
import pyautogui
import pygetwindow
try:
    from ultralytics import YOLO
except ImportError:
    from src.common.simulate import YOLO
import pygame
import pygame.camera as pycam
from src.common.simulate import FakeCamera
from src.common.constants import CAMERA_RESOLUTION, CLASSIFIER_PATH, TRAINING_MODE_CAMERA_SIZE
from src.vision.vsrc.constants import DATA, REALVNC_WINDOW_NAME, BORDER_WIDTH, LOWER_THRESHOLD, UPPER_THRESHOLD
class Vision_Handler:
    def __init__(self, enableInference:bool=False, captureVNC:bool=False, resolution:tuple=CAMERA_RESOLUTION) -> None:
        self.enableInference = enableInference
        self.captureVNC = captureVNC
        self.currentFrame = pygame.Surface(resolution)
        if self.enableInference:
            self.model = YOLO(CLASSIFIER_PATH)
        else:
            self.model = None
        # Camera setup
        self.fakeCamera = FakeCamera(0)
        self.realCamera = None
        # Class label font
        self.labelMap = {k["num_label"] : k["label"] for k in DATA.values()}
        self.labelFont = pygame.font.SysFont("Roboto", 20)
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

    def get_frame(self) -> pygame.Surface:
        """
        Get the current frame from the camera
        """
        if self.captureVNC:
            self.currentFrame = self.capture_vnc()
        else:
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
        # Classifier
        imgData = pygame.surfarray.array3d(frame)
        results = self.model.predict(imgData, verbose=False)
        for result in results:
            clsList = result.obb.cls.tolist()
            # For every box
            for i, _ in enumerate(clsList):
                box = result.obb.xyxyxyxy[i].tolist()
                cls = clsList[i]
                conf = result.obb.conf[i].tolist()
                # Draw the bounding box
                pygame.draw.lines(frame, (255, 0, 0), True, box, 2)
                # Draw the class
                label = self.labelFont.render(f"{self.labelMap[cls]}:{conf:.2f}", True, (255, 0, 0))
                frame.blit(label, (box[0], box[1]))
        return frame

    def destroy(self) -> None:
        """
        Destroy the camera
        """
        if self.realCamera is not None:
            self.realCamera.stop()
        return

if __name__ == "__main__":
    INFERENCE = True
    CAPTURE_VNC = True
    TRAINING_MODE = True
    # Derived
    RES = TRAINING_MODE_CAMERA_SIZE if TRAINING_MODE else CAMERA_RESOLUTION
    FRAMERATE = 30
    pygame.init()
    vision = Vision_Handler(INFERENCE, CAPTURE_VNC, RES)
    display = pygame.display.set_mode(RES, (pygame.RESIZABLE | pygame.SCALED))
    clk = pygame.time.Clock()
    while True:
        clk.tick(FRAMERATE)
        vision.inference()
        display.blit(vision.currentFrame, (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                vision.destroy()
                pygame.quit()
                exit()

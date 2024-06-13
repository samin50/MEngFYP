import multiprocessing
import numpy
import time
import cv2
from src.common.constants import BOUNDING_BOX_COLOR
from src.vision.vsrc.constants import DATA
MAP = {k["num_label"] : k["label"] for k in DATA.values()}
TESTING = False
try:
    from ultralytics import YOLO
    print("Using ultralytics YOLO!")
except ImportError:
    from src.common.simulate import YOLO
    print("Using simulated YOLO!")
# pylint:disable=all

def inference_process(frameQueue: multiprocessing.Queue, resultQueue: multiprocessing.Queue, busyInference: multiprocessing.Event, modelPath: str) -> None:
    """
    Process to handle inference
    """
    model = YOLO(modelPath)
    print("Loaded YOLO model!")
    while True:
        print("Waiting for frame")
        frame = cv2.cvtColor(frameQueue.get(), cv2.COLOR_BGR2RGB)
        start = time.time()
        print("Got frame")
        # Inference
        res = model.predict(frame)
        result = draw_results(frame, res)
        resultQueue.put(result)
        busyInference.clear()
        print(f"Inference took {time.time()-start:.2f}s")

def draw_results(frame: numpy.ndarray, results) -> numpy.ndarray:
    """
    Draw the results on the frame
    """
    blackBackground = numpy.zeros_like(frame)
    frameHeight, frameWidth = frame.shape[:2]
    clsList = []
    conf = 0
    croppedImage = None
    # For every box
    for result in results:
        # Get the class
        clsList = result.obb.cls.tolist()
        if len(clsList) == 0:
            continue
        box = numpy.array(result.obb.xyxyxyxy[0].cpu(), dtype=numpy.int0)
        # Only for testing
        if TESTING:
            cv2.imshow("frame", cv2.polylines(frame.copy(), [box], isClosed=True, color=BOUNDING_BOX_COLOR, thickness=3))
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        # Crop the image
        croppedImage = crop_image(frame, box).swapaxes(0, 1)
        # Draw the polygon
        frame = cv2.polylines(blackBackground, [box], isClosed=True, color=BOUNDING_BOX_COLOR, thickness=3)
        # Draw the class
        fontScale = 1.5
        fontThickness = 2
        conf = result.obb.conf[0]
        cls = MAP[clsList[0]]
        label = f"{cls}:{conf:.2f}"
        labelSize, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontThickness)
        x, y = box[0]
        topLeftCorner = (x, y - labelSize[1] - 10)
        bottomRightCorner = (x + labelSize[0], y - 10)
        # Ensure the label is on screen
        topLeftCorner = (max(0, min(topLeftCorner[0], frameWidth - labelSize[0])), 
                         max(0, min(topLeftCorner[1], frameHeight - labelSize[1] - 10)))
        bottomRightCorner = (topLeftCorner[0] + labelSize[0], topLeftCorner[1] + labelSize[1] + 10)
        # Draw a filled rectangle for the label background
        cv2.rectangle(blackBackground, topLeftCorner, bottomRightCorner, BOUNDING_BOX_COLOR, cv2.FILLED)
        # Draw the label text
        cv2.putText(blackBackground, label, (topLeftCorner[0], topLeftCorner[1] + labelSize[1]), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 255, 255), fontThickness)
        print(f"{conf:.2f} {cls}")
        conf = float(f"{conf:.2f}")*100
    return (frame.swapaxes(0, 1), croppedImage, conf, cls)

def crop_image(frame: numpy.ndarray, box: numpy.ndarray) -> numpy.ndarray:
    """
    Crop the image to the bounding box
    """
    # Ensure box is an integer type
    box = box.astype(int)
    
    # Compute dimensions
    height = int(numpy.linalg.norm(box[0] - box[1]))
    width = int(numpy.linalg.norm(box[1] - box[2]))
    
    # Compute center
    center = numpy.mean(box, axis=0).astype(int)
    
    # Compute rotation angle
    angle = numpy.degrees(numpy.arctan2(box[1, 1] - box[0, 1], box[1, 0] - box[0, 0]))
    rotation_matrix = cv2.getRotationMatrix2D((int(center[0]), int(center[1])), angle, 1.0)
    
    # Apply the rotation to the image
    rotated_image = cv2.warpAffine(frame, rotation_matrix, (frame.shape[1], frame.shape[0]))
    
    # Get the bounding box in the rotated image
    x, y = center - [width // 2, height // 2]
    
    # Ensure the coordinates are within the bounds of the image
    x = max(0, x)
    y = max(0, y)
    x_end = min(rotated_image.shape[1], x + width)
    y_end = min(rotated_image.shape[0], y + height)
    
    # Crop the image
    croppedImage = rotated_image[y:y_end, x:x_end]
    
    # Change image colour
    croppedImage = cv2.cvtColor(croppedImage, cv2.COLOR_RGB2BGR)
    
    return croppedImage
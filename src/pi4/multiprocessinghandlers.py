import multiprocessing
try:
    from ultralytics import YOLO
    print("Using ultralytics YOLO!")
except ImportError:
    from src.common.simulate import YOLO
    print("Using simulated YOLO!")
# pylint:disable=all

def inference_process(frameQueue: multiprocessing.Queue, resultQueue: multiprocessing.Queue, inferenceComplete: multiprocessing.Event, modelPath: str) -> None:
    """
    Process to handle inference
    """
    print("loaded model")
    model = YOLO(modelPath)
    while True:
        frame = frameQueue.get()
        # Inference
        # result = self.model.predict(frame)
        result = frame
        resultQueue.put(result)
        inferenceComplete.set()
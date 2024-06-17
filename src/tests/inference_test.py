from ultralytics import YOLO
from os import getcwd, path

MODEL_PATH = "./src/vision/models/final/classifier.pt"
VAL_PATH = "./src/vision/models/recipes/dataset_desc.yaml"
TEST_PATH = "./src/vision/models/recipes/dataset_desc_test.yaml"
print(path.exists(VAL_PATH), getcwd())

# Load model, perform validation
model = YOLO(MODEL_PATH)
metrics = model.val(data=TEST_PATH, batch=1)

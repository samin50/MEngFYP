from deepsparse import benchmark_model
# print(getcwd())
MODEL_PATH = "./src/vision/models/final/classifier.onnx"

# Load pipeline
# result = benchmark_model(MODEL_PATH, engine="onnxruntime", batch_size=1, time=60)
result = benchmark_model(MODEL_PATH, engine="deepsparse", batch_size=1, time=60)
print(result)

import tflite_runtime.interpreter as tflite

# Load the TFLite model
model_path = './build/float_model/f_model.tflite'
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get details of all layers
for i in range(len(interpreter.get_tensor_details())):
    print(interpreter.get_tensor_details()[i])

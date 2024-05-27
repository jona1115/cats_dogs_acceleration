###############################################################################################
#  
#  Created by: Jonathan Tan (jona1115@iastate.edu, github.com/jona1115)
#  Date      : 5/27/2024
#  
###########################################################################################
#  
#  @file catdog_inference_tflite.py
#  @comments This file is written by, or with the help of, ChatGPT.
#  
#  MODIFICATION HISTORY:
# 
#  Ver   Who       Date	      Changes
#  ----- --------- ---------- ----------------------------------------------
#  1.00	 Jonathan  5/27/2024
#  
###############################################################################################


import time
import numpy as np
from PIL import Image
from vaitrace_py import vai_tracepoint
import tflite_runtime.interpreter as tflite

# Load the TFLite model
model_path = './build/float_model/f_model.tflite'
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get input and output tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load and prepare the image
@vai_tracepoint
def load_and_prepare_image(image_path, target_size=(250, 200)):
    img = Image.open(image_path)
    img = img.resize(target_size)
    img_array = np.array(img).astype('float32') / 255.0  # Normalize to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # Make 'batch' of 1
    return img_array

# Perform inference
def run_inference(image_path):
    img_array = load_and_prepare_image(image_path)
    
    # Set the tensor to point to the input data to be inferred
    interpreter.set_tensor(input_details[0]['index'], img_array)
    
    # Run the inference
    interpreter.invoke()
    
    # Extract the output data
    predictions = interpreter.get_tensor(output_details[0]['index'])
    return predictions

# Example usage
image_path = './build/dataset/test/cat.1035.jpg'  # Update this to the path of your image

start_time = time.time()  # Simple profiling

predictions = run_inference(image_path)

end_time = time.time()  # Simple profiling
print(f"Inference took {end_time - start_time}s to run.")  # Simple profiling

print("Results:")
print(predictions)

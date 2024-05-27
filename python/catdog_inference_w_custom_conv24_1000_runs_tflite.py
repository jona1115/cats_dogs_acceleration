###############################################################################################
#  
#  Created by: Jonathan Tan (jona1115@iastate.edu, github.com/jona1115)
#  Date      : 5/18/2024
#  
###########################################################################################
#  
#  @file catdog_inference_w_custom_conv24_1000_runs.py
#  @comments Part of this file is written by, or with the help of, ChatGPT.
#  
#  MODIFICATION HISTORY:
# 
#  Ver   Who       Date	      Changes
#  ----- --------- ---------- ----------------------------------------------
#  1.00	 Jonathan  5/18/2024
#  
###############################################################################################

# Compile c code and run: g++ -fPIC -shared -o lib_run_conv2d_24.so run_conv2d_24.cpp && python catdog_inference_w_custom_conv24_1000_runs.py

import time
import ctypes
import os
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
from vaitrace_py import vai_tracepoint

# Load the TensorFlow Lite model
tflite_model_path = './build/float_model/f_model.tflite'
interpreter = tflite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load the shared library for custom layer
cpp_lib = ctypes.CDLL('./lib_run_conv2d_24.so')

# Define the return type and argument types for the C++ function
cpp_lib.run_conv2d_24.restype = None  # Output array is modified directly
cpp_lib.run_conv2d_24.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float32, flags="C_CONTIGUOUS"), ctypes.c_int,  # input and size
    np.ctypeslib.ndpointer(dtype=np.float32, flags="C_CONTIGUOUS"), ctypes.c_int,  # weights and size
    np.ctypeslib.ndpointer(dtype=np.float32, flags="C_CONTIGUOUS"), ctypes.c_int,  # bias and size
    ctypes.c_int, ctypes.c_int,  # inputHeight, inputWidth
    ctypes.c_int, ctypes.c_int,  # outputHeight, outputWidth
    ctypes.c_int, ctypes.c_int,  # kernelHeight, kernelWidth
    ctypes.c_int, ctypes.c_int,  # channelsIn, channelsOut
    np.ctypeslib.ndpointer(dtype=np.float32, flags="C_CONTIGUOUS"), ctypes.c_int  # output and size
]

def conv2d_24_cpp(input_tensor, weights, bias):
    input_data = input_tensor.astype(np.float32)
    if len(input_data.shape) != 3:
        raise ValueError(f"Expected input_data to have 3 dimensions (height, width, channels), got {len(input_data.shape)} dimensions.")
    
    height, width, channels = input_data.shape
    weights_flat = weights.flatten().astype(np.float32)
    bias_flat = bias.flatten().astype(np.float32)
    input_size = input_data.size
    weights_size = weights_flat.size
    bias_size = bias_flat.size

    outputHeight, outputWidth = 7, 8
    channelsOut = 128
    output_size = outputHeight * outputWidth * channelsOut
    output_data = np.zeros(output_size, dtype=np.float32)

    cpp_lib.run_conv2d_24(
        input_data, input_size,
        weights_flat, weights_size,
        bias_flat, bias_size,
        height, width,
        outputHeight, outputWidth,
        3, 3,
        channels, channelsOut,
        output_data, output_size
    )

    return output_data.reshape((outputHeight, outputWidth, channelsOut))

@vai_tracepoint
def load_and_prepare_image(image_path, target_size=(250, 200)):
    img = Image.open(image_path)
    img = img.resize(target_size)
    img_array = np.array(img).astype('float32') / 255.0  # Normalize to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # Make 'batch' of 1
    return img_array

def run_inference_with_custom_layer(image_path, interpreter, weights, biases):
    input_data = load_and_prepare_image(image_path)

    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Get intermediate output from the layer before conv2d_24 (assuming it's index 91)
    intermediate_output = interpreter.get_tensor(91)

    # Debugging: Check the shape of the intermediate output
    print(f"Intermediate output shape: {intermediate_output.shape}")

    if len(intermediate_output.shape) != 4:
        raise ValueError(f"Expected intermediate_output to have 4 dimensions (batch, height, width, channels), got {len(intermediate_output.shape)} dimensions.")

    # Remove the batch dimension
    intermediate_output = np.squeeze(intermediate_output, axis=0)

    # Process conv2d_24 with custom C++ library
    output_from_cpp = conv2d_24_cpp(intermediate_output, weights, biases)
    output_from_cpp = output_from_cpp.reshape((1, 7, 8, 128))

    # Set the output of the custom layer as input to the next stage in the model
    interpreter.set_tensor(input_details[0]['index'], output_from_cpp)
    interpreter.invoke()
    final_output = interpreter.get_tensor(output_details[0]['index'])

    return final_output

def run_full_inference_tflite(image_path):
    img_array = load_and_prepare_image(image_path)
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])
    return predictions

# Example usage
# Note: You will need to manually extract and handle the weights and biases for conv2d_24 layer from your TensorFlow model beforehand.
weights = np.load('weights_conv2d_24.npy')  # Assuming weights are saved in a NumPy array
biases = np.load('biases_conv2d_24.npy')    # Assuming biases are saved in a NumPy array

image_dir = './build/dataset/test/'

total_inference_time_with_custom_layer_s = 0
total_inference_time_without_custom_layer_s = 0
MAX_IMAGES_COUNT_TO_RUN = 100
counter = 0

for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.jpg')):
        file_path = os.path.join(image_dir, filename)
        print(f"Running inference on {filename} ({counter})...")

        start_time = time.time()
        final_output_with_custom_layer = run_inference_with_custom_layer(file_path, interpreter, weights, biases)
        end_time = time.time()
        total_inference_time_with_custom_layer_s += end_time - start_time

        start_time = time.time()
        predictions_without_custom_layer = run_full_inference_tflite(file_path)
        end_time = time.time()
        total_inference_time_without_custom_layer_s += end_time - start_time

        counter += 1
        if counter >= MAX_IMAGES_COUNT_TO_RUN:
            break

print(f"Stats:")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time with custom layer: {(total_inference_time_with_custom_layer_s / MAX_IMAGES_COUNT_TO_RUN):.3f}s")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time w/o custom layer: {(total_inference_time_without_custom_layer_s / MAX_IMAGES_COUNT_TO_RUN):.3f}s")

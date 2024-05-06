###############################################################################################
#  
#  Created by: Jonathan Tan (jona1115@iastate.edu, github.com/jona1115)
#  Date      : 5/5/2024
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
#  1.00	 Jonathan  5/5/2024
#  
###############################################################################################

# Compile c code and run: g++ -fPIC -shared -o lib_run_conv2d_24.so run_conv2d_24.cpp && python catdog_inference_w_custom_conv24_1000_runs.py

import time
import ctypes
import os

import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
from PIL import Image
from tensorflow.python.profiler import trace

from vaitrace_py import vai_tracepoint

# Load the pre-trained model
model_path = './build/float_model/f_model.h5'
model = load_model(model_path)

# Because we want to accelerate only conv2d_24

# Create a new model that ends at the layer before the one you want to implement in C++
model_up_to_conv2d_23 = Model(inputs=model.input, outputs=model.get_layer('conv2d_23').output)

# Assuming you have another model for the layers after your C++ layer
model_after_conv2d_24 = Model(inputs=model.get_layer('conv2d_24').output, outputs=model.output)

# Load the shared library
cpp_lib = ctypes.CDLL('./lib_run_conv2d_24.so')

# Note layer conv24's info:  conv2d_24 (Conv2D)             (None, 7, 8, 128)    147584      ['add_4[0][0]']                  

# Define the return type and argument types
# cpp_lib.run_conv2d_24.restype = ctypes.POINTER(ctypes.c_float * 7*8*128)  # Define output size accordingly
cpp_lib.run_conv2d_24.restype = None  # As the output array is passed in and modified directly
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

# Call the C++ convolution function
def conv2d_24_cpp(input_tensor, weights, bias):
    # Ensure input tensor is squeezed to remove the batch dimension if necessary
    input_data = np.squeeze(input_tensor, axis=0).astype(np.float32)
    
    # Flatten the weights and biases
    weights_flat = weights.flatten().astype(np.float32)
    bias_flat = bias.flatten().astype(np.float32)

    # Calculate the sizes of the arrays
    input_size = input_data.size
    weights_size = weights_flat.size
    bias_size = bias_flat.size

    # Prepare the output array
    outputHeight, outputWidth = 7, 8  # These should match the expected output dimensions of the C++ layer
    channelsOut = 128  # This should match the number of filters in the conv2d_24 layer
    output_size = outputHeight * outputWidth * channelsOut
    output_data = np.zeros(output_size, dtype=np.float32)  # Output array that will be modified by the C++ function

    # Dimensions of the input data
    height, width, channels = input_data.shape

    # Call the C++ function with all parameters, including sizes
    cpp_lib.run_conv2d_24(
        input_data, input_size,  # Input array and its size
        weights_flat, weights_size,  # Weights array and its size
        bias_flat, bias_size,  # Bias array and its size
        height, width,  # Dimensions of the input
        outputHeight, outputWidth,  # Dimensions of the output
        3, 3,  # Assuming kernel height and width are both 3
        channels, channelsOut,  # Number of input and output channels
        output_data, output_size  # Output array and its size
    )

    # Reshape the flat output array back to the expected tensor shape
    return output_data.reshape((outputHeight, outputWidth, channelsOut))

# Function to load and preprocess the image
def load_and_prepare_image(image_path, target_size=(200, 250)):
    # Load image using Keras' load_img function
    img = load_img(image_path, target_size=target_size)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Reshape to (1, height, width, channels)
    img_array /= 255.0  # Normalize to [0,1]
    return img_array

# Perform inference
def run_inference(image_path):
    # img_array = load_and_prepare_image(image_path)
    # with trace.Trace('trace_inference', step_num=1, _r=1):
    #     predictions = model.predict(img_array, callbacks=[tensorboard_callback])
    # return predictions
    # ^^ for profiling
    # vv no profiling
    img_array = load_and_prepare_image(image_path)
    predictions = model.predict(img_array)
    return predictions


image_dir = './build/dataset/test/'

# Simple profiling
total_inference_time_with_custom_layer_s = 0
total_inference_time_without_custom_layer_s = 0

MAX_IMAGES_COUNT_TO_RUN = 100
counter = 0

# Loop through the files in the directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.jpg')):
        # Construct full file path
        file_path = os.path.join(image_dir, filename)
                
        # Grab image
        image_path = file_path                              # Non custom use this (might not be right)
        input_data = load_and_prepare_image(image_path)     # Custon use this (might not be right)

        print(f"Running inference on {filename} ({counter})...")

        start_time = time.time() # Simple profiling
        # Get weights and biases from the specific layer
        conv2d_24_layer = model.get_layer('conv2d_24')
        weights, biases = conv2d_24_layer.get_weights()

        # Run inference with custom conv2d_24 c++ implementation
        input_tensor = model_up_to_conv2d_23.predict(input_data)
        output_from_cpp = conv2d_24_cpp(input_tensor, weights, biases)
        output_from_cpp = output_from_cpp.reshape((1, 7, 8, 128))
        final_output = model_after_conv2d_24.predict(output_from_cpp)
        end_time = time.time() # Simple profiling
        total_inference_time_with_custom_layer_s += end_time - start_time # Simple profiling

        # Run inference w/o custom conv2d_24 c++ implementation
        start_time = time.time() # Simple profiling
        predictions = run_inference(image_path)
        end_time = time.time() # Simple profiling
        total_inference_time_without_custom_layer_s += end_time - start_time # Simple profiling

        # Non custom vs custom accuracy
        # final_output[0][0]

    counter += 1
    if (counter >= MAX_IMAGES_COUNT_TO_RUN):
        break

print(f"Stats:")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time with custom layer: {(total_inference_time_with_custom_layer_s/MAX_IMAGES_COUNT_TO_RUN):6.3f}s")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time w/o custom layer : {(total_inference_time_without_custom_layer_s/MAX_IMAGES_COUNT_TO_RUN):6.3f}s")
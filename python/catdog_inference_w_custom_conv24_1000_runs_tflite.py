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
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model, Model

# Load the TensorFlow Lite model
tflite_model_path = './build/float_model/f_model.tflite'
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
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
    input_data = np.squeeze(input_tensor, axis=0).astype(np.float32)
    weights_flat = weights.flatten().astype(np.float32)
    bias_flat = bias.flatten().astype(np.float32)
    input_size = input_data.size
    weights_size = weights_flat.size
    bias_size = bias_flat.size

    outputHeight, outputWidth = 7, 8
    channelsOut = 128
    output_size = outputHeight * outputWidth * channelsOut
    output_data = np.zeros(output_size, dtype=np.float32)

    height, width, channels = input_data.shape

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

def load_and_prepare_image(image_path, target_size=(250, 200)):
    img = Image.open(image_path)
    img = img.resize(target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array

def run_inference_with_custom_layer(image_path, model_up_to_conv2d_23, model_after_conv2d_24, weights, biases):
    input_data = load_and_prepare_image(image_path)
    input_tensor = model_up_to_conv2d_23.predict(input_data)
    output_from_cpp = conv2d_24_cpp(input_tensor, weights, biases)
    output_from_cpp = output_from_cpp.reshape((1, 7, 8, 128))
    final_output = model_after_conv2d_24.predict(output_from_cpp)
    return final_output

def run_full_inference_tflite(image_path):
    img_array = load_and_prepare_image(image_path)
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])
    return predictions

# Example usage
model_path = './build/float_model/f_model.h5'
model = load_model(model_path)

model_up_to_conv2d_23 = Model(inputs=model.input, outputs=model.get_layer('conv2d_23').output)
model_after_conv2d_24 = Model(inputs=model.get_layer('conv2d_24').output, outputs=model.output)

conv2d_24_layer = model.get_layer('conv2d_24')
weights, biases = conv2d_24_layer.get_weights()

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
        final_output_with_custom_layer = run_inference_with_custom_layer(
            file_path, model_up_to_conv2d_23, model_after_conv2d_24, weights, biases)
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
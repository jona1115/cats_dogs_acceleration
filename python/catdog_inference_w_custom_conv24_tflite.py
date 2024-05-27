import time
import ctypes
import os

import numpy as np
from PIL import Image
from tflite_runtime.interpreter import Interpreter, load_delegate

# Load the TensorFlow Lite model
model_path = './build/float_model/f_model.tflite'
interpreter = Interpreter(model_path)
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load the shared library
cpp_lib = ctypes.CDLL('./lib_run_conv2d_24.so')

# Define the return type and argument types for the shared library
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
    print(f"Input data shape (after squeeze): {input_data.shape}")
    
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
    return output_data.reshape((1, outputHeight, outputWidth, channelsOut))

# Function to load and preprocess the image
def load_and_prepare_image(image_path, target_size=(250, 200)):
    # Load image using PIL
    img = Image.open(image_path)
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)  # Reshape to (1, height, width, channels)
    img_array /= 255.0  # Normalize to [0,1]
    return img_array

# Perform inference
def run_inference(image_path):
    img_array = load_and_prepare_image(image_path)
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])
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
        image_path = file_path
        input_data = load_and_prepare_image(image_path)

        print(f"Running inference on {filename} ({counter})...")

        start_time = time.time() # Simple profiling

        # Get weights and biases from the specific layer (assuming you have access to them)
        # You might need to hard-code these or extract them from another source
        weights = np.load('./weights_conv2d_24.npy')  # Example path
        biases = np.load('./biases_conv2d_24.npy')    # Example path

        # Run inference with custom conv2d_24 c++ implementation
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        # Print the details of the output tensors
        print(f"Output details: {output_details}")
        
        intermediate_output = interpreter.get_tensor(output_details[0]['index'])
        
        print(f"Intermediate output shape: {intermediate_output.shape}")
        
        if len(intermediate_output.shape) != 4:
            raise ValueError(f"Unexpected shape for intermediate output: {intermediate_output.shape}")
        
        output_from_cpp = conv2d_24_cpp(intermediate_output, weights, biases)
        
        print(f"Output from C++ shape: {output_from_cpp.shape}")
        
        # Here you should properly set the output_from_cpp as input to the next part of the model.
        # Assuming the model is split into multiple parts, or you can continue using the interpreter.

        # Assuming you have a way to run the rest of the model
        # interpreter.set_tensor(input_details_next_part['index'], output_from_cpp)
        # interpreter.invoke()
        # final_output = interpreter.get_tensor(output_details_next_part['index'])

        # Temporarily setting the output to be the same as cpp output for example
        final_output = output_from_cpp
        
        end_time = time.time() # Simple profiling
        total_inference_time_with_custom_layer_s += end_time - start_time # Simple profiling

        # Run inference w/o custom conv2d_24 c++ implementation
        start_time = time.time() # Simple profiling
        predictions = run_inference(image_path)
        end_time = time.time() # Simple profiling
        total_inference_time_without_custom_layer_s += end_time - start_time # Simple profiling

    counter += 1
    if (counter >= MAX_IMAGES_COUNT_TO_RUN):
        break

print(f"Stats:")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time with custom layer: {(total_inference_time_with_custom_layer_s/MAX_IMAGES_COUNT_TO_RUN):6.3f}s")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time w/o custom layer : {(total_inference_time_without_custom_layer_s/MAX_IMAGES_COUNT_TO_RUN):6.3f}s")

import time
import ctypes
import os
import numpy as np
from PIL import Image
from tflite_runtime.interpreter import Interpreter

# Load the TensorFlow Lite model for the first part up to conv2d_23
model_path_up_to_conv2d_23 = './build/float_model_up_to_conv2d_23.tflite'
interpreter_up_to_conv2d_23 = Interpreter(model_path_up_to_conv2d_23)
interpreter_up_to_conv2d_23.allocate_tensors()

# Load the TensorFlow Lite model for the second part after conv2d_24
model_path_after_conv2d_24 = './build/float_model_after_conv2d_24.tflite'
interpreter_after_conv2d_24 = Interpreter(model_path_after_conv2d_24)
interpreter_after_conv2d_24.allocate_tensors()

# Get input and output details for both interpreters
input_details_up_to_conv2d_23 = interpreter_up_to_conv2d_23.get_input_details()
output_details_up_to_conv2d_23 = interpreter_up_to_conv2d_23.get_output_details()

input_details_after_conv2d_24 = interpreter_after_conv2d_24.get_input_details()
output_details_after_conv2d_24 = interpreter_after_conv2d_24.get_output_details()

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
    input_data = np.squeeze(input_tensor, axis=0).astype(np.float32)
    print(f"Input data shape (after squeeze): {input_data.shape}")

    weights_flat = weights.flatten().astype(np.float32)
    bias_flat = bias.flatten().astype(np.float32)

    input_size = input_data.size
    weights_size = weights_flat.size
    bias_size = bias_flat.size

    outputHeight, outputWidth = 13, 16  # Ensure this matches the expected output dimensions
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

    return output_data.reshape((1, outputHeight, outputWidth, channelsOut))

def load_and_prepare_image(image_path, target_size=(250, 200)):
    img = Image.open(image_path)
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array

def run_inference(image_path):
    img_array = load_and_prepare_image(image_path)
    interpreter_up_to_conv2d_23.set_tensor(input_details_up_to_conv2d_23[0]['index'], img_array)
    interpreter_up_to_conv2d_23.invoke()
    intermediate_output = interpreter_up_to_conv2d_23.get_tensor(output_details_up_to_conv2d_23[0]['index'])
    return intermediate_output

image_dir = './build/dataset/test/'

total_inference_time_with_custom_layer_s = 0
total_inference_time_without_custom_layer_s = 0

MAX_IMAGES_COUNT_TO_RUN = 1
counter = 0

for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.jpg')):
        file_path = os.path.join(image_dir, filename)
        image_path = file_path
        input_data = load_and_prepare_image(image_path)

        print(f"Running inference on {filename} ({counter})...")

        start_time = time.time()

        weights = np.load('./weights_conv2d_24.npy')
        biases = np.load('./biases_conv2d_24.npy')

        intermediate_output = run_inference(image_path)
        print(f"Intermediate output shape: {intermediate_output.shape}")

        if len(intermediate_output.shape) != 4:
            raise ValueError(f"Unexpected shape for intermediate output: {intermediate_output.shape}")

        output_from_cpp = conv2d_24_cpp(intermediate_output, weights, biases)
        print(f"Output from C++ shape: {output_from_cpp.shape}")

        # Run inference after conv2d_24 using the second part of the model
        interpreter_after_conv2d_24.set_tensor(input_details_after_conv2d_24[0]['index'], output_from_cpp)
        interpreter_after_conv2d_24.invoke()
        final_output = interpreter_after_conv2d_24.get_tensor(output_details_after_conv2d_24[0]['index'])

        end_time = time.time()
        total_inference_time_with_custom_layer_s += end_time - start_time

        # Print the final output which should be the class probabilities
        print("Final predictions with custom layer:", final_output)

        start_time = time.time()
        interpreter_up_to_conv2d_23.set_tensor(input_details_up_to_conv2d_23[0]['index'], input_data)
        interpreter_up_to_conv2d_23.invoke()
        predictions = interpreter_up_to_conv2d_23.get_tensor(output_details_up_to_conv2d_23[0]['index'])
        end_time = time.time()
        total_inference_time_without_custom_layer_s += end_time - start_time

    counter += 1
    if (counter >= MAX_IMAGES_COUNT_TO_RUN):
        break

print(f"Stats:")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time with custom layer: {(total_inference_time_with_custom_layer_s/MAX_IMAGES_COUNT_TO_RUN):6.3f}s")
print(f"Average ({MAX_IMAGES_COUNT_TO_RUN}) inference time w/o custom layer : {(total_inference_time_without_custom_layer_s/MAX_IMAGES_COUNT_TO_RUN):6.3f}s")

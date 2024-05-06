###############################################################################################
#  
#  Created by: Jonathan Tan (jona1115@iastate.edu, github.com/jona1115)
#  Date      : 5/5/2024
#  
###########################################################################################
#  
#  @file catdog_inference.py
#  @comments This file is written by, or with the help of, ChatGPT.
#  
#  MODIFICATION HISTORY:
# 
#  Ver   Who       Date	      Changes
#  ----- --------- ---------- ----------------------------------------------
#  1.00	 Jonathan  5/5/2024
#  
###############################################################################################


import time

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
from tensorflow.python.profiler import trace


from vaitrace_py import vai_tracepoint

# Load the pre-trained model
model_path = './build/float_model/f_model.h5'  # Update this to the path of your H5 file
model = load_model(model_path)

# # Set up TensorBoard logging
# log_dir = "./tensorboard/profile/"
# tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1, profile_batch='10,15')

# Load and prepare the image
@vai_tracepoint
def load_and_prepare_image(image_path, target_size=(250, 200)):
    img = Image.open(image_path)
    img = img.resize(target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Make 'batch' of 1
    img_array /= 255.  # Normalize to [0,1]
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

# Example usage
image_path = './build/dataset/test/cat.1035.jpg'  # Update this to the path of your image

start_time = time.time() # Simple profiling

predictions = run_inference(image_path)

end_time = time.time() # Simple profiling
print(f"Inference took {end_time - start_time}s to run.") # Simple profiling

print("Results:")
print(predictions)

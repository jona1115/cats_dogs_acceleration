###############################################################################################
#  
#  Created by: Jonathan Tan (jona1115@iastate.edu, github.com/jona1115)
#  Date      : 5/18/2024
#  
###########################################################################################
#  
#  @file tf_to_tflite.py
#  @comments Part of this file is written by, or with the help of, ChatGPT.
#  
#  MODIFICATION HISTORY:
# 
#  Ver   Who       Date	      Changes
#  ----- --------- ---------- ----------------------------------------------
#  1.00	 Jonathan  5/18/2024
#  
###############################################################################################

import tensorflow as tf

# Load the pre-trained model
model_path = './build/quant_model/q_model.h5'  # Update this to the path of your H5 file
model = tf.keras.models.load_model(model_path)

# Convert the model to TensorFlow Lite format
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model
tflite_model_path = './build/quant_model/q_model.tflite'
with open(tflite_model_path, 'wb') as f:
    f.write(tflite_model)

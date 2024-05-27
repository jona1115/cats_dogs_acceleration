import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Path to your TensorFlow model
model_path = './build/float_model/f_model.h5'

# Load the TensorFlow model
model = load_model(model_path)

# Get the conv2d_24 layer
conv2d_24_layer = model.get_layer('conv2d_24')

# Extract weights and biases
weights, biases = conv2d_24_layer.get_weights()

# Save the weights and biases as .npy files
np.save('weights_conv2d_24.npy', weights)
np.save('biases_conv2d_24.npy', biases)

print("Weights and biases have been extracted and saved.")

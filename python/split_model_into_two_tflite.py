import tensorflow as tf

# Load the original model
model_path = './build/float_model/f_model.h5'
model = tf.keras.models.load_model(model_path)

# Create a model that ends at 'conv2d_23'
model_up_to_conv2d_23 = tf.keras.Model(inputs=model.input, outputs=model.get_layer('conv2d_23').output)

# Create a model that starts at 'conv2d_24'
input_tensor_after_conv2d_24 = tf.keras.Input(shape=model.get_layer('conv2d_24').input.shape[1:])
output_tensor_after_conv2d_24 = model.layers[-1](input_tensor_after_conv2d_24)
model_after_conv2d_24 = tf.keras.Model(inputs=input_tensor_after_conv2d_24, outputs=output_tensor_after_conv2d_24)

# Convert the model that ends at 'conv2d_23' to TensorFlow Lite
converter_up_to_conv2d_23 = tf.lite.TFLiteConverter.from_keras_model(model_up_to_conv2d_23)
tflite_model_up_to_conv2d_23 = converter_up_to_conv2d_23.convert()

# Save the TensorFlow Lite model to a file
with open('./build/float_model_up_to_conv2d_23.tflite', 'wb') as f:
    f.write(tflite_model_up_to_conv2d_23)

# Convert the model that starts at 'conv2d_24' to TensorFlow Lite
converter_after_conv2d_24 = tf.lite.TFLiteConverter.from_keras_model(model_after_conv2d_24)
tflite_model_after_conv2d_24 = converter_after_conv2d_24.convert()

# Save the TensorFlow Lite model to a file
with open('./build/float_model_after_conv2d_24.tflite', 'wb') as f:
    f.write(tflite_model_after_conv2d_24)

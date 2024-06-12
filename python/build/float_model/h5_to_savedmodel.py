import tensorflow as tf

# Load your Keras model
model = tf.keras.models.load_model('f_model.h5')

# Save it as a TensorFlow SavedModel
model.save('saved_model')


# How to
### 1. Convert your ML model to ONNX
1. In the Vitis AI docker container (if you don't know what it is, see [here](https://github.com/jona1115/cats_dogs_acceleration/tree/main/python#how-to-run)) , run:  
    `python -m tf2onnx.convert --opset 16 --tflite ./build/float_model/f_model.tflite --output ./build/float_model/f_model.onnx`  
    You should get a f_model.onnx in the `build/float_model` folder.
2. I copied it over to this directory.

### 2. Run the Tensil compiler
1. `docker pull tensilai/tensil:latest`
2. In this dir (step1): `docker run -v $(pwd):/work -w /work -it tensilai/tensil:latest bash`
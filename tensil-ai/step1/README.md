# How to
### 1. Convert your ML model to ONNX
1. We need to first turn our h5 into a "saved_model", there is a script in `build/float_model/h5_to_savedmodel.py` to do that. Once you run it, you will get a .onnx model.
2. In the Vitis AI docker container (if you don't know what it is, see [here](https://github.com/jona1115/cats_dogs_acceleration/tree/main/python#how-to-run)) , run:  
    `python -m tf2onnx.convert --saved-model saved_model/ --opset 10 --output f_model.onnx --opset 10`, Note: opset needs to be [9,10] for Tensil to work  
    You should get a f_model.onnx in the `build/float_model` folder.
3. I copied it over to this directory.

### 2. Run the Tensil compiler
1. `docker pull tensilai/tensil:latest`
2. In this dir (step1): `docker run -v $(pwd):/work -w /work -it tensilai/tensil:latest bash`
3. In the docker, run: `tensil compile -a /demo/arch/ultra96v2.tarch -m f_model.onnx -o "activation_30" -s true` (Not working atm)
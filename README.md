# Cats Dogs Acceleration

Hardware Accelerators for Machine Learning have always fascinated me. In this project, I want to try different things to accelerate an ML model. My model of choice is the [Kaggle Dogs vs Cats project](https://www.kaggle.com/c/dogs-vs-cats/data), I will try to make the inference faster using different techniques.

The goal of this project:
1. Obtain the model and create the Python inference code to run the inference. (Done, you can find them in [python/])(https://github.com/jona1115/cats_dogs_acceleration/tree/main/python)
2. Pick a layer in the model and, write a C++ implementation of that layer, and use that code when running inference. (Done, you can find them in [python/](https://github.com/jona1115/cats_dogs_acceleration/tree/main/python))
3. Create a Petalinux build for running development environment. (Done, you can find the guide in [documentation/vivadoTRD_and_Petalinux/](https://github.com/jona1115/cats_dogs_acceleration/tree/main/documentations/vivadoTRD_and_Petalinux))
4. Use VHDL to write an accelerator for that layer.
5. Use [Tensil](https://www.tensil.ai/) to create custom HW accelerator for the model.
6. Use Vitis HLS to create a custom accelerator for that layer.
7. Turn the Tensorflow model into an xmodel and run it on my Kria board's DPU.

> The layer I choose is `conv2d_24`, this layer has the most amount of parameters, and I suspect that it is the slowest layer.

There are several parts to this project:
1. [Python code](https://github.com/jona1115/cats_dogs_acceleration/tree/main/python)
2. [Vivado XSA and Petalinux build](https://github.com/jona1115/cats_dogs_acceleration/blob/main/documentations/vivadoTRD_and_Petalinux/README.md)
3. VHDL IP (Coming soon...)
4. Other coming soon...

Current Progress:
| Date | Progress |
| --- | --- |
| 5/17/2024 | Configure Petalinux to have necessary dependencies for development |
| 5/14/2024 | Created bootable Petalinux build for development |
| 5/5/2024 | Created inference code that uses custom c++ layer implementation |
| 3/28/2024 | Followed Vitis-AI tutorial and trained the model |
